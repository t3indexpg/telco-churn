"""
Etapa `preparar` del pipeline DVC.

Lee los datos crudos de Telco Customer Churn (Kaggle / IBM), aplica la
limpieza definida en la exploración (notebooks/01_exploracion_datos.ipynb)
y guarda un dataset limpio y enriquecido en data/processed/.

Uso:
    python src/data/make_dataset.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
PARAMS = yaml.safe_load(open(ROOT / "params.yaml", encoding="utf-8"))

RAW = ROOT / PARAMS["data"]["raw"]
OUT = ROOT / PARAMS["data"]["processed"]

SERVICIOS = [
    "PhoneService", "MultipleLines", "OnlineSecurity", "OnlineBackup",
    "DeviceProtection", "TechSupport", "StreamingTV", "StreamingMovies",
]


def limpiar(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # 1. Formatos: quitar espacios en texto
    obj = [c for c in df.columns if df[c].dtype == object or pd.api.types.is_string_dtype(df[c])]
    df[obj] = df[obj].apply(lambda s: s.str.strip())

    # 2. Duplicados (por registro y por llave)
    df = df.drop_duplicates().drop_duplicates(subset="customerID")

    # 3. TotalCharges viene como texto; los 11 vacíos son clientes con tenure = 0
    #    (aún no facturados), por lo que se imputan con 0 (imputación lógica).
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    mask = df["TotalCharges"].isna() & (df["tenure"] == 0)
    df.loc[mask, "TotalCharges"] = 0.0

    # 4. Homogeneizar categorías redundantes
    #    'No internet service' / 'No phone service' equivalen a 'No' en el servicio
    for c in SERVICIOS:
        df[c] = df[c].replace({"No internet service": "No", "No phone service": "No"})

    # 5. Tipos consistentes
    df["SeniorCitizen"] = df["SeniorCitizen"].map({0: "No", 1: "Yes"})
    df["Churn"] = df["Churn"].map({"No": 0, "Yes": 1}).astype(int)
    return df


def enriquecer(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["tenure_grupo"] = pd.cut(
        df["tenure"], bins=[-1, 6, 12, 24, 48, 72],
        labels=["0-6m", "7-12m", "13-24m", "25-48m", "49-72m"],
    ).astype(str)
    df["num_servicios"] = (df[SERVICIOS] == "Yes").sum(axis=1)
    df["tiene_internet"] = (df["InternetService"] != "No").map({True: "Yes", False: "No"})
    df["pago_automatico"] = df["PaymentMethod"].str.contains("automatic").map({True: "Yes", False: "No"})
    # Cargo promedio histórico vs. cargo actual (señal de aumento de precio)
    df["cargo_promedio_hist"] = np.where(df["tenure"] > 0, df["TotalCharges"] / df["tenure"], df["MonthlyCharges"])
    df["delta_cargo"] = df["MonthlyCharges"] - df["cargo_promedio_hist"]
    return df


def main() -> None:
    df_raw = pd.read_csv(RAW)
    df = enriquecer(limpiar(df_raw))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Crudo: {df_raw.shape} -> Limpio: {df.shape} | nulos: {int(df.isna().sum().sum())}")
    print(f"Guardado en {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
