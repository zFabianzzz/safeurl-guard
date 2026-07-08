"""
train_model.py
Entrena un modelo Random Forest con el dataset de URLs y guarda el modelo.

USO:
    python train_model.py --data ../../dataset_with_all_features_v2.csv

El modelo se guarda en backend/model/rf_model.joblib
"""
import argparse
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
import json

# Features usadas para entrenar (mismas que extrae feature_extractor.py)
FEATURE_COLUMNS = [
    "web_is_live", "web_security_score", "web_forms_count", "web_password_fields",
    "web_has_login", "web_ssl_valid", "url_len",
    "@", "?", "-", "=", ".", "#", "%", "+", "$", "!", "*", ",", "//",
    "digits", "letters", "abnormal_url", "https", "Shortining_Service",
    "having_ip_address", "defac_has_hacked_terms", "defac_has_suspicious_ext",
    "defac_path_depth", "defac_is_deep_path", "defac_path_underscores",
    "defac_is_gov_edu", "defac_has_index_php", "defac_has_option_param",
    "phish_has_brand", "phish_brand_in_subdomain", "phish_brand_in_path",
    "phish_hyphen_count", "phish_digit_count", "phish_long_domain",
    "phish_many_subdomains", "phish_suspicious_tld", "phish_keyword_count",
    "phish_has_redirect", "phish_param_count", "phish_encoded_chars",
    "enh_urgency_count", "enh_security_count", "enh_brand_count",
    "enh_brand_hijack", "enh_subdomain_count", "enh_long_path",
    "enh_many_params", "enh_suspicious_tld",
    "adv_domain_ngram_entropy", "adv_path_entropy", "adv_consonant_ratio",
    "adv_vowel_ratio", "adv_digit_ratio", "adv_subdomain_count",
    "adv_avg_subdomain_len", "adv_token_count", "adv_avg_token_length",
]

# Mapeo label numérico -> nombre de clase
LABEL_MAP = {
    0.0: "benign",
    1.0: "defacement",
    2.0: "phishing",
    3.0: "malware"
}

# Mapeo clase -> nivel de riesgo base (0-100)
RISK_MAP = {
    "benign": 5,
    "defacement": 65,
    "phishing": 88,
    "malware": 95
}


def load_data(csv_path: str, sample_size: int = None):
    print(f"Cargando dataset desde: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"  Total filas: {len(df)}")
    print(f"  Distribución de clases:\n{df['type'].value_counts()}\n")

    # Verificar que las columnas necesarias existen
    missing = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Columnas faltantes en el dataset: {missing}")

    # Si el dataset es muy grande, hacer un muestreo estratificado
    if sample_size and len(df) > sample_size:
        print(f"  Reduciendo a {sample_size} muestras (estratificado)...")
        df = df.groupby("type", group_keys=False).apply(
            lambda x: x.sample(min(len(x), sample_size // 4), random_state=42)
        ).reset_index(drop=True)
        print(f"  Muestras tras reducción: {len(df)}")

    return df


def train(csv_path: str, output_dir: str, sample_size: int = None):
    df = load_data(csv_path, sample_size)

    # Preparar X e y
    X = df[FEATURE_COLUMNS].fillna(0)
    y = df["type"]  # benign, phishing, malware, defacement

    # Dividir en train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Train: {len(X_train)} | Test: {len(X_test)}")
    print("Entrenando Random Forest...")

    # Modelo Random Forest optimizado
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=25,
        min_samples_split=5,
        min_samples_leaf=2,
        max_features="sqrt",
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,  # usar todos los núcleos
        verbose=1
    )

    model.fit(X_train, y_train)

    # Evaluación
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.4f}")
    print("\nReporte de clasificación:")
    print(classification_report(y_test, y_pred))

    # Importancia de features (top 15)
    feat_imp = sorted(
        zip(FEATURE_COLUMNS, model.feature_importances_),
        key=lambda x: x[1], reverse=True
    )[:15]
    print("\nTop 15 features más importantes:")
    for name, imp in feat_imp:
        print(f"  {name}: {imp:.4f}")

    # Guardar modelo y metadata
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "rf_model.joblib")
    joblib.dump(model, model_path, compress=3)
    print(f"\nModelo guardado en: {model_path}")

    # Guardar metadata del modelo
    metadata = {
        "accuracy": round(acc, 4),
        "feature_columns": FEATURE_COLUMNS,
        "classes": list(model.classes_),
        "label_map": LABEL_MAP,
        "risk_map": RISK_MAP,
        "n_estimators": 200,
        "training_samples": len(X_train),
    }
    meta_path = os.path.join(output_dir, "model_metadata.json")
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata guardada en: {meta_path}")

    return model_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenar modelo SafeURL Guard")
    parser.add_argument("--data", required=True, help="Ruta al CSV del dataset")
    parser.add_argument("--output", default="model", help="Directorio de salida del modelo")
    parser.add_argument(
        "--sample", type=int, default=200000,
        help="Muestras máximas (0=todas). Default: 200000 para rapidez"
    )
    args = parser.parse_args()

    sample = args.sample if args.sample > 0 else None
    train(args.data, args.output, sample_size=sample)
