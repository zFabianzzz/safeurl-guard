"""
merge_and_retrain.py
Combina el dataset original con URLs benignas de Majestic Million
y reentrena el modelo Random Forest.

USO desde la carpeta backend/:
    python merge_and_retrain.py \
        --original "C:/Users/Stealth/Downloads/dataset_with_all_features v2.csv" \
        --majestic "C:/Users/Stealth/Downloads/majestic_million.csv" \
        --sample 100000
"""
import argparse
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import json
import math
import re
from urllib.parse import urlparse, parse_qs
from collections import Counter

# ─── Features ─────────────────────────────────────────────────────────────────

KNOWN_BRANDS = [
    "google","facebook","apple","microsoft","amazon","paypal","netflix",
    "instagram","twitter","youtube","whatsapp","linkedin","dropbox",
    "banco","bank","bbva","santander","scotiabank","bcp","interbank",
    "visa","mastercard","ebay","steam","outlook","gmail"
]
SUSPICIOUS_TLDS = [".tk",".ml",".ga",".cf",".gq",".xyz",".top",".click",
                   ".loan",".work",".date",".racing",".stream"]
SUSPICIOUS_EXTENSIONS = [".exe",".zip",".rar",".bat",".cmd",".sh"]
URGENCY_WORDS = ["urgent","urgente","immediately","inmediato","alert","alerta",
                 "warning","limited","expire","expira","verify","verificar",
                 "confirm","confirmar","suspended","suspendido"]
SECURITY_WORDS = ["secure","seguro","security","seguridad","safe","protec",
                  "login","signin","account","cuenta","password","contraseña",
                  "update","actualizar","verify","verification"]
HACKED_TERMS = ["hacked","owned","pwned","defaced","hack","h4ck","r00t"]

def _entropy(text):
    if not text: return 0.0
    freq = Counter(text)
    length = len(text)
    return -sum((c/length)*math.log2(c/length) for c in freq.values())

def extract_features_from_url(url):
    url_lower = url.lower()
    parsed = urlparse(url if "://" in url else "https://" + url)
    domain = parsed.netloc.lower() or url_lower.split("/")[0]
    path = parsed.path.lower()
    query = parsed.query.lower()
    full = url_lower

    https = 1 if url_lower.startswith("https://") else 0
    having_ip = 1 if re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", domain) else 0
    path_parts = [p for p in path.split("/") if p]
    defac_path_depth = len(path_parts)
    domain_parts = domain.replace("www.","").split(".")
    defac_is_gov_edu = 1 if any(p in ["gov","edu","gob"] for p in domain_parts) else 0
    main_parts = domain.split(".")
    subdomain_str = ".".join(main_parts[:-2]) if len(main_parts) > 2 else ""
    subdomains = [s for s in subdomain_str.split(".") if s]
    path_chars = path.replace("/","")
    consonants = sum(1 for c in path_chars if c.isalpha() and c not in "aeiou")
    vowels = sum(1 for c in path_chars if c in "aeiou")
    total_alpha = consonants + vowels
    digits_in_path = sum(c.isdigit() for c in path_chars)
    tokens = re.split(r"[/\-_?=&.]+", url)
    tokens = [t for t in tokens if t]
    params = parse_qs(parsed.query)
    short_services = ["bit.ly","tinyurl","goo.gl","t.co","ow.ly","is.gd","buff.ly"]

    return {
        "web_is_live": 1,
        "web_security_score": https * 50,
        "web_forms_count": 0,
        "web_password_fields": 0,
        "web_has_login": 1 if any(w in full for w in ["login","signin","account","cuenta"]) else 0,
        "web_ssl_valid": https,
        "url_len": len(url),
        "@": url.count("@"),
        "?": url.count("?"),
        "-": url.count("-"),
        "=": url.count("="),
        ".": url.count("."),
        "#": url.count("#"),
        "%": url.count("%"),
        "+": url.count("+"),
        "$": url.count("$"),
        "!": url.count("!"),
        "*": url.count("*"),
        ",": url.count(","),
        "//": url.count("//"),
        "digits": sum(c.isdigit() for c in url),
        "letters": sum(c.isalpha() for c in url),
        "abnormal_url": 1 if "@" in url else 0,
        "https": https,
        "Shortining_Service": 1 if any(s in domain for s in short_services) else 0,
        "having_ip_address": having_ip,
        "defac_has_hacked_terms": 1 if any(t in full for t in HACKED_TERMS) else 0,
        "defac_has_suspicious_ext": 1 if any(e in path for e in SUSPICIOUS_EXTENSIONS) else 0,
        "defac_path_depth": defac_path_depth,
        "defac_is_deep_path": 1 if defac_path_depth > 4 else 0,
        "defac_path_underscores": sum(p.count("_") for p in path_parts),
        "defac_is_gov_edu": defac_is_gov_edu,
        "defac_has_index_php": 1 if "index.php" in path else 0,
        "defac_has_option_param": 1 if "option=" in query else 0,
        "phish_has_brand": 1 if any(b in domain for b in KNOWN_BRANDS) else 0,
        "phish_brand_in_subdomain": 1 if any(b in subdomain_str for b in KNOWN_BRANDS) else 0,
        "phish_brand_in_path": 1 if any(b in path for b in KNOWN_BRANDS) else 0,
        "phish_hyphen_count": url.count("-"),
        "phish_digit_count": sum(c.isdigit() for c in url),
        "phish_long_domain": 1 if len(domain) > 30 else 0,
        "phish_many_subdomains": 1 if domain.count(".") > 3 else 0,
        "phish_suspicious_tld": 1 if any(domain.endswith(t) for t in SUSPICIOUS_TLDS) else 0,
        "phish_keyword_count": sum(1 for w in SECURITY_WORDS if w in full),
        "phish_has_redirect": 1 if "redirect" in full or "return=" in full else 0,
        "phish_param_count": len(params),
        "phish_encoded_chars": url.count("%"),
        "enh_urgency_count": sum(1 for w in URGENCY_WORDS if w in full),
        "enh_security_count": sum(1 for w in SECURITY_WORDS if w in full),
        "enh_brand_count": sum(1 for b in KNOWN_BRANDS if b in full),
        "enh_brand_hijack": 1 if any(b in subdomain_str for b in KNOWN_BRANDS) else 0,
        "enh_subdomain_count": len(subdomains),
        "enh_long_path": 1 if len(path) > 50 else 0,
        "enh_many_params": 1 if len(params) > 3 else 0,
        "enh_suspicious_tld": 1 if any(domain.endswith(t) for t in SUSPICIOUS_TLDS) else 0,
        "adv_domain_ngram_entropy": _entropy(domain.replace(".","").replace("-","")),
        "adv_path_entropy": _entropy(path),
        "adv_consonant_ratio": consonants/total_alpha if total_alpha > 0 else 0.0,
        "adv_vowel_ratio": vowels/total_alpha if total_alpha > 0 else 0.0,
        "adv_digit_ratio": digits_in_path/len(path_chars) if path_chars else 0.0,
        "adv_subdomain_count": len(subdomains),
        "adv_avg_subdomain_len": sum(len(s) for s in subdomains)/len(subdomains) if subdomains else 0.0,
        "adv_token_count": len(tokens),
        "adv_avg_token_length": sum(len(t) for t in tokens)/len(tokens) if tokens else 0.0,
    }

FEATURE_COLUMNS = [
    "web_is_live","web_security_score","web_forms_count","web_password_fields",
    "web_has_login","web_ssl_valid","url_len",
    "@","?","-","=",".","#","%","+","$","!","*",",","//",
    "digits","letters","abnormal_url","https","Shortining_Service",
    "having_ip_address","defac_has_hacked_terms","defac_has_suspicious_ext",
    "defac_path_depth","defac_is_deep_path","defac_path_underscores",
    "defac_is_gov_edu","defac_has_index_php","defac_has_option_param",
    "phish_has_brand","phish_brand_in_subdomain","phish_brand_in_path",
    "phish_hyphen_count","phish_digit_count","phish_long_domain",
    "phish_many_subdomains","phish_suspicious_tld","phish_keyword_count",
    "phish_has_redirect","phish_param_count","phish_encoded_chars",
    "enh_urgency_count","enh_security_count","enh_brand_count",
    "enh_brand_hijack","enh_subdomain_count","enh_long_path",
    "enh_many_params","enh_suspicious_tld",
    "adv_domain_ngram_entropy","adv_path_entropy","adv_consonant_ratio",
    "adv_vowel_ratio","adv_digit_ratio","adv_subdomain_count",
    "adv_avg_subdomain_len","adv_token_count","adv_avg_token_length",
]

# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--original", required=True)
    parser.add_argument("--majestic", required=True)
    parser.add_argument("--sample", type=int, default=100000)
    parser.add_argument("--output", default="model")
    args = parser.parse_args()

    # 1. Cargar dataset original
    print("Cargando dataset original...")
    df_orig = pd.read_csv(args.original)
    print(f"  Filas originales: {len(df_orig)}")
    print(f"  Distribución:\n{df_orig['type'].value_counts()}\n")

    # 2. Cargar Majestic y extraer features
    print(f"Cargando Majestic Million (tomando {args.sample} dominios)...")
    df_maj = pd.read_csv(args.majestic).head(args.sample)

    print(f"  Extrayendo features de {len(df_maj)} dominios...")
    rows = []
    errores = 0
    for i, row in df_maj.iterrows():
        domain = str(row["Domain"]).strip()
        url = "https://" + domain
        try:
            feats = extract_features_from_url(url)
            feats["type"] = "benign"
            feats["label"] = 0.0
            rows.append(feats)
        except Exception:
            errores += 1

    df_new_benign = pd.DataFrame(rows)
    print(f"  Features extraídas: {len(df_new_benign)} ({errores} errores ignorados)")

    # 3. Combinar — solo columnas necesarias
    print("Combinando datasets...")
    cols_needed = FEATURE_COLUMNS + ["type", "label"]

    # Asegurarse que el original tiene todas las columnas
    df_orig_trim = df_orig[cols_needed].copy()
    df_new_trim = df_new_benign[cols_needed].copy()

    df_combined = pd.concat([df_orig_trim, df_new_trim], ignore_index=True)
    print(f"  Total combinado: {len(df_combined)}")
    print(f"  Nueva distribución:\n{df_combined['type'].value_counts()}\n")

    # 4. Muestreo estratificado — preservar columna type
    print("Aplicando muestreo estratificado...")
    grupos = []
    for tipo, grupo in df_combined.groupby("type"):
        n = min(len(grupo), 50000)
        grupos.append(grupo.sample(n, random_state=42))

    df_sample = pd.concat(grupos, ignore_index=True)
    print(f"  Muestras para entrenamiento: {len(df_sample)}")
    print(f"  Distribución final:\n{df_sample['type'].value_counts()}\n")

    # 5. Entrenar
    X = df_sample[FEATURE_COLUMNS].fillna(0)
    y = df_sample["type"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Train: {len(X_train)} | Test: {len(X_test)}")
    print("Entrenando Random Forest...")

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=25,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
        verbose=1,
    )
    model.fit(X_train, y_train)

    # 6. Evaluar
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.4f}")
    print(classification_report(y_test, y_pred))

    # 7. Guardar
    os.makedirs(args.output, exist_ok=True)
    model_path = os.path.join(args.output, "rf_model.joblib")
    joblib.dump(model, model_path, compress=3)
    print(f"Modelo guardado en: {model_path}")

    meta = {
        "accuracy": round(acc, 4),
        "feature_columns": FEATURE_COLUMNS,
        "classes": list(model.classes_),
        "training_samples": len(X_train),
        "majestic_added": len(df_new_benign),
    }
    with open(os.path.join(args.output, "model_metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)
    print("¡Modelo actualizado correctamente!")

if __name__ == "__main__":
    main()
