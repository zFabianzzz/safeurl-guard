"""
feature_extractor.py
Extrae las mismas features usadas en el dataset para pasarlas al modelo Random Forest.
"""
import re
import math
from urllib.parse import urlparse, parse_qs
from collections import Counter

# Marcas conocidas para detectar brand hijacking / phishing
KNOWN_BRANDS = [
    "google", "facebook", "apple", "microsoft", "amazon", "paypal", "netflix",
    "instagram", "twitter", "youtube", "whatsapp", "linkedin", "dropbox",
    "banco", "bank", "bbva", "santander", "scotiabank", "bcp", "interbank",
    "visa", "mastercard", "ebay", "steam", "outlook", "gmail"
]

SUSPICIOUS_TLDS = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top", ".click",
                   ".loan", ".work", ".date", ".racing", ".stream"]

SUSPICIOUS_EXTENSIONS = [".exe", ".zip", ".rar", ".bat", ".cmd", ".sh", ".php", ".js"]

URGENCY_WORDS = ["urgent", "urgente", "immediately", "inmediato", "alert", "alerta",
                 "warning", "limited", "expire", "expira", "verify", "verificar",
                 "confirm", "confirmar", "suspended", "suspendido"]

SECURITY_WORDS = ["secure", "seguro", "security", "seguridad", "safe", "protec",
                  "login", "signin", "account", "cuenta", "password", "contraseña",
                  "update", "actualizar", "verify", "verification"]

HACKED_TERMS = ["hacked", "owned", "pwned", "defaced", "hack", "h4ck", "r00t"]


def _entropy(text: str) -> float:
    """Calcula entropía de Shannon de un string."""
    if not text:
        return 0.0
    freq = Counter(text)
    length = len(text)
    return -sum((c / length) * math.log2(c / length) for c in freq.values())


def extract_features(url: str) -> dict:
    """
    Extrae todas las features del dataset a partir de una URL raw.
    Devuelve un dict con las mismas columnas usadas para entrenar.
    """
    url_lower = url.lower()
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()
    query = parsed.query.lower()
    full = url_lower

    # --- Básicas ---
    url_len = len(url)
    count_at = url.count("@")
    count_q = url.count("?")
    count_dash = url.count("-")
    count_eq = url.count("=")
    count_dot = url.count(".")
    count_hash = url.count("#")
    count_pct = url.count("%")
    count_plus = url.count("+")
    count_dollar = url.count("$")
    count_excl = url.count("!")
    count_star = url.count("*")
    count_comma = url.count(",")
    count_dslash = url.count("//")
    digits = sum(c.isdigit() for c in url)
    letters = sum(c.isalpha() for c in url)

    # --- SSL / HTTPS ---
    https = 1 if url_lower.startswith("https://") else 0
    web_ssl_valid = https  # proxy: si es https asumimos SSL válido

    # --- IP en URL ---
    having_ip_address = 1 if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain) else 0

    # --- URL anormal (dominio ≠ host real) ---
    abnormal_url = 0
    if domain and not re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain):
        # Si el dominio contiene el path (URL mal formada)
        abnormal_url = 1 if "@" in url else 0

    # --- Shortening service ---
    short_services = ["bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly", "is.gd",
                      "buff.ly", "adf.ly", "tr.im", "short.io", "cutt.ly"]
    shortining_service = 1 if any(s in domain for s in short_services) else 0

    # --- Defacement features ---
    defac_has_hacked_terms = 1 if any(t in full for t in HACKED_TERMS) else 0
    path_parts = [p for p in path.split("/") if p]
    defac_path_depth = len(path_parts)
    defac_is_deep_path = 1 if defac_path_depth > 4 else 0
    defac_path_underscores = sum(p.count("_") for p in path_parts)
    domain_parts = domain.replace("www.", "").split(".")
    defac_is_gov_edu = 1 if any(p in ["gov", "edu", "gob", "edu.pe", "gob.pe", "mil"] for p in domain_parts) else 0
    defac_has_index_php = 1 if "index.php" in path else 0
    defac_has_option_param = 1 if "option=" in query else 0
    defac_has_suspicious_ext = 1 if any(ext in path for ext in SUSPICIOUS_EXTENSIONS) else 0

    # --- Phishing features ---
    phish_has_brand = 1 if any(b in domain for b in KNOWN_BRANDS) else 0
    # Brand en subdominio (no en dominio principal)
    main_domain_parts = domain.split(".")
    subdomain_str = ".".join(main_domain_parts[:-2]) if len(main_domain_parts) > 2 else ""
    phish_brand_in_subdomain = 1 if any(b in subdomain_str for b in KNOWN_BRANDS) else 0
    phish_brand_in_path = 1 if any(b in path for b in KNOWN_BRANDS) else 0
    phish_hyphen_count = count_dash
    phish_digit_count = digits
    phish_long_domain = 1 if len(domain) > 30 else 0
    phish_many_subdomains = 1 if domain.count(".") > 3 else 0
    phish_suspicious_tld = 1 if any(domain.endswith(t) for t in SUSPICIOUS_TLDS) else 0
    phish_keyword_count = sum(1 for w in SECURITY_WORDS if w in full)
    phish_has_redirect = 1 if "redirect" in full or "return=" in full or "url=" in full else 0
    params = parse_qs(parsed.query)
    phish_param_count = len(params)
    phish_encoded_chars = url.count("%") + url.count("\\x")

    # --- Enhanced features ---
    enh_urgency_count = sum(1 for w in URGENCY_WORDS if w in full)
    enh_security_count = sum(1 for w in SECURITY_WORDS if w in full)
    enh_brand_count = sum(1 for b in KNOWN_BRANDS if b in full)
    enh_brand_hijack = 1 if phish_brand_in_subdomain or phish_brand_in_path else 0
    subdomains = [s for s in subdomain_str.split(".") if s]
    enh_subdomain_count = len(subdomains)
    enh_long_path = 1 if len(path) > 50 else 0
    enh_many_params = 1 if phish_param_count > 3 else 0
    enh_suspicious_tld = phish_suspicious_tld

    # --- Advanced / entropy features ---
    adv_domain_ngram_entropy = _entropy(domain.replace(".", "").replace("-", ""))
    adv_path_entropy = _entropy(path)
    path_chars = path.replace("/", "")
    consonants = sum(1 for c in path_chars if c.isalpha() and c not in "aeiou")
    vowels = sum(1 for c in path_chars if c in "aeiou")
    total_alpha = consonants + vowels
    adv_consonant_ratio = consonants / total_alpha if total_alpha > 0 else 0.0
    adv_vowel_ratio = vowels / total_alpha if total_alpha > 0 else 0.0
    adv_digit_ratio = sum(c.isdigit() for c in path_chars) / len(path_chars) if path_chars else 0.0
    adv_subdomain_count = enh_subdomain_count
    adv_avg_subdomain_len = (sum(len(s) for s in subdomains) / len(subdomains)) if subdomains else 0.0
    tokens = re.split(r"[/\-_?=&.]+", url)
    tokens = [t for t in tokens if t]
    adv_token_count = len(tokens)
    adv_avg_token_length = (sum(len(t) for t in tokens) / len(tokens)) if tokens else 0.0

    # Web features (no disponibles en tiempo real sin crawling — usamos proxies)
    web_is_live = 1  # asumimos que si el usuario está visitando, está activa
    web_security_score = https * 50  # proxy básico
    web_forms_count = 0
    web_password_fields = 0
    web_has_login = 1 if any(w in full for w in ["login", "signin", "account", "cuenta"]) else 0

    return {
        "web_is_live": web_is_live,
        "web_security_score": web_security_score,
        "web_forms_count": web_forms_count,
        "web_password_fields": web_password_fields,
        "web_has_login": web_has_login,
        "web_ssl_valid": web_ssl_valid,
        "url_len": url_len,
        "@": count_at,
        "?": count_q,
        "-": count_dash,
        "=": count_eq,
        ".": count_dot,
        "#": count_hash,
        "%": count_pct,
        "+": count_plus,
        "$": count_dollar,
        "!": count_excl,
        "*": count_star,
        ",": count_comma,
        "//": count_dslash,
        "digits": digits,
        "letters": letters,
        "abnormal_url": abnormal_url,
        "https": https,
        "Shortining_Service": shortining_service,
        "having_ip_address": having_ip_address,
        "defac_has_hacked_terms": defac_has_hacked_terms,
        "defac_has_suspicious_ext": defac_has_suspicious_ext,
        "defac_path_depth": defac_path_depth,
        "defac_is_deep_path": defac_is_deep_path,
        "defac_path_underscores": defac_path_underscores,
        "defac_is_gov_edu": defac_is_gov_edu,
        "defac_has_index_php": defac_has_index_php,
        "defac_has_option_param": defac_has_option_param,
        "phish_has_brand": phish_has_brand,
        "phish_brand_in_subdomain": phish_brand_in_subdomain,
        "phish_brand_in_path": phish_brand_in_path,
        "phish_hyphen_count": phish_hyphen_count,
        "phish_digit_count": phish_digit_count,
        "phish_long_domain": phish_long_domain,
        "phish_many_subdomains": phish_many_subdomains,
        "phish_suspicious_tld": phish_suspicious_tld,
        "phish_keyword_count": phish_keyword_count,
        "phish_has_redirect": phish_has_redirect,
        "phish_param_count": phish_param_count,
        "phish_encoded_chars": phish_encoded_chars,
        "enh_urgency_count": enh_urgency_count,
        "enh_security_count": enh_security_count,
        "enh_brand_count": enh_brand_count,
        "enh_brand_hijack": enh_brand_hijack,
        "enh_subdomain_count": enh_subdomain_count,
        "enh_long_path": enh_long_path,
        "enh_many_params": enh_many_params,
        "enh_suspicious_tld": enh_suspicious_tld,
        "adv_domain_ngram_entropy": adv_domain_ngram_entropy,
        "adv_path_entropy": adv_path_entropy,
        "adv_consonant_ratio": adv_consonant_ratio,
        "adv_vowel_ratio": adv_vowel_ratio,
        "adv_digit_ratio": adv_digit_ratio,
        "adv_subdomain_count": adv_subdomain_count,
        "adv_avg_subdomain_len": adv_avg_subdomain_len,
        "adv_token_count": adv_token_count,
        "adv_avg_token_length": adv_avg_token_length,
    }
