"""
analyzer.py
Servicio que carga el modelo Random Forest y analiza URLs.
"""
import os
import json
import logging
import numpy as np
import pandas as pd
import joblib
from urllib.parse import urlparse

from .feature_extractor import extract_features

logger = logging.getLogger(__name__)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")
MODEL_PATH = os.path.join(MODEL_DIR, "rf_model.joblib")
META_PATH = os.path.join(MODEL_DIR, "model_metadata.json")

RISK_BASE = {
    "benign": 5,
    "defacement": 65,
    "phishing": 88,
    "malware": 95,
}

THRESHOLD_BLOCK = 70
THRESHOLD_WARNING = 40

# Dominios siempre seguros (whitelist)
SAFE_DOMAINS = {
    "google.com", "www.google.com", "accounts.google.com",
    "youtube.com", "www.youtube.com",
    "github.com", "www.github.com",
    "microsoft.com", "www.microsoft.com", "live.com", "outlook.com",
    "apple.com", "www.apple.com",
    "wikipedia.org", "www.wikipedia.org",
    "stackoverflow.com", "www.stackoverflow.com",
    "anthropic.com", "www.anthropic.com",
    "amazon.com", "www.amazon.com",
    "facebook.com", "www.facebook.com", "m.facebook.com",
    "instagram.com", "www.instagram.com",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "whatsapp.com", "web.whatsapp.com", "www.whatsapp.com",
    "linkedin.com", "www.linkedin.com",
    "netflix.com", "www.netflix.com",
    "spotify.com", "www.spotify.com",
    "reddit.com", "www.reddit.com",
    "twitch.tv", "www.twitch.tv",
    "tiktok.com", "www.tiktok.com",
    "canva.com", "www.canva.com",
    "notion.so", "www.notion.so",
    "discord.com", "www.discord.com",
    "dropbox.com", "www.dropbox.com",
    "drive.google.com", "docs.google.com", "mail.google.com",
    "undc.edu.pe", "aula.undc.edu.pe", "sivireno.undc.edu.pe",
    "chrome.google.com", "localhost", "newtab",
}

# TLDs que indican dominios educativos o gubernamentales confiables
TRUSTED_TLDS = (
    ".edu.pe", ".gob.pe", ".edu", ".gov", ".mil",
    ".edu.ar", ".edu.co", ".edu.mx", ".gob.mx", ".gov.co",
)


class URLAnalyzer:
    def __init__(self):
        self.model = None
        self.metadata = {}
        self.feature_columns = []
        self._load_model()

    def _load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(META_PATH):
            try:
                self.model = joblib.load(MODEL_PATH)
                with open(META_PATH) as f:
                    self.metadata = json.load(f)
                self.feature_columns = self.metadata.get("feature_columns", [])
                logger.info("✅ Modelo Random Forest cargado correctamente")
                logger.info(f"   Accuracy: {self.metadata.get('accuracy', '?')}")
            except Exception as e:
                logger.error(f"Error cargando modelo: {e}")
                self.model = None
        else:
            logger.warning("⚠️  Modelo no encontrado. Usando analizador heurístico básico.")

    def _is_whitelisted(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        if url.startswith("chrome://") or url.startswith("edge://") or url.startswith("about:"):
            return True
        return domain in SAFE_DOMAINS

    def _is_trusted_tld(self, domain: str) -> bool:
        """Verifica si el dominio pertenece a un TLD educativo o gubernamental confiable."""
        domain_lower = domain.lower()
        return any(domain_lower.endswith(tld) for tld in TRUSTED_TLDS)

    def _calculate_risk_from_proba(self, proba: dict, predicted_class: str) -> int:
        p_benign = proba.get("benign", 0)
        p_malware = proba.get("malware", 0)
        p_phishing = proba.get("phishing", 0)
        p_defacement = proba.get("defacement", 0)

        risk_score = (
            p_malware * 95 +
            p_phishing * 88 +
            p_defacement * 65 +
            p_benign * 5
        )
        return min(100, int(risk_score))

    def _heuristic_analysis(self, url: str) -> dict:
        import re
        riesgo = 0
        url_lower = url.lower()
        parsed = urlparse(url)

        if not url_lower.startswith("https://"):
            riesgo += 20
        if len(url) > 75:
            riesgo += 15
        if re.search(r"\d+\.\d+\.\d+\.\d+", url):
            riesgo += 30
        if url.count("-") >= 3:
            riesgo += 15
        if url.count(".") >= 5:
            riesgo += 10

        palabras = ["login", "verify", "secure", "bank", "banco", "update",
                    "password", "cuenta", "gratis", "premio", "phishing",
                    "free", "win", "winner", "claim"]
        for p in palabras:
            if p in url_lower:
                riesgo += 12

        sus_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".xyz", ".top"]
        if any(url_lower.endswith(t) for t in sus_tlds):
            riesgo += 20

        riesgo = min(100, riesgo)

        # Reducir riesgo para dominios educativos/gubernamentales
        domain = parsed.netloc.lower()
        if self._is_trusted_tld(domain):
            riesgo = min(riesgo, 35)

        if riesgo >= THRESHOLD_BLOCK:
            clasificacion = "Phishing"
            accion = "Bloqueado"
        elif riesgo >= THRESHOLD_WARNING:
            clasificacion = "Sospechosa"
            accion = "Advertencia"
        else:
            clasificacion = "Segura"
            accion = "Permitido"

        return {
            "url": url,
            "dominio": parsed.netloc,
            "clasificacion": clasificacion,
            "riesgo": riesgo,
            "accion": accion,
            "modelo": "heuristico",
            "probabilidades": {},
        }

    def analyze(self, url: str) -> dict:
        parsed = urlparse(url)
        domain = parsed.netloc

        # 1. Whitelist exacta
        if self._is_whitelisted(url):
            return {
                "url": url,
                "dominio": domain,
                "clasificacion": "Segura",
                "riesgo": 2,
                "accion": "Permitido",
                "modelo": "whitelist",
                "probabilidades": {"benign": 1.0},
            }

        # 2. Sin modelo, usar heurística
        if self.model is None:
            return self._heuristic_analysis(url)

        # 3. Extraer features y predecir
        try:
            features = extract_features(url)
            X = pd.DataFrame([features])[self.feature_columns]
            X = X.fillna(0)
        except Exception as e:
            logger.error(f"Error extrayendo features: {e}")
            return self._heuristic_analysis(url)

        try:
            classes = self.model.classes_
            proba_array = self.model.predict_proba(X)[0]
            proba = dict(zip(classes, proba_array.tolist()))
            predicted_class = classes[np.argmax(proba_array)]

            riesgo = self._calculate_risk_from_proba(proba, predicted_class)

            # Determinar clasificación y acción base
            if predicted_class == "malware":
                clasificacion = "Malware"
                accion = "Bloqueado" if riesgo >= THRESHOLD_BLOCK else "Advertencia"
            elif predicted_class == "phishing":
                clasificacion = "Phishing"
                accion = "Bloqueado" if riesgo >= THRESHOLD_BLOCK else "Advertencia"
            elif predicted_class == "defacement":
                clasificacion = "Defacement"
                accion = "Bloqueado" if riesgo >= THRESHOLD_BLOCK else "Advertencia"
            else:
                clasificacion = "Segura"
                accion = "Permitido"

            # Reducir riesgo para dominios educativos y gubernamentales
            if self._is_trusted_tld(domain):
                riesgo = min(riesgo, 35)
                if accion == "Bloqueado":
                    accion = "Advertencia"
                    clasificacion = "Sospechosa"

            return {
                "url": url,
                "dominio": domain,
                "clasificacion": clasificacion,
                "riesgo": riesgo,
                "accion": accion,
                "modelo": "random_forest",
                "probabilidades": {k: round(v, 4) for k, v in proba.items()},
            }

        except Exception as e:
            logger.error(f"Error en predicción del modelo: {e}")
            return self._heuristic_analysis(url)


_analyzer_instance = None


def get_analyzer() -> URLAnalyzer:
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = URLAnalyzer()
    return _analyzer_instance