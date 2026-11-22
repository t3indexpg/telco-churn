import os
import json
import gc
from pathlib import Path

import pandas as pd
import joblib
import mlflow

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix
)
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

BASE = Path(os.getenv("TELCO_DATA_DIR", "/app"))
train = pd.read_csv(BASE / "train.csv")
test = pd.read_csv(BASE / "test.csv")

X_train = train.drop(columns=["Churn", "customerID"])
y_train = train["Churn"]
X_test = test.drop(columns=["Churn", "customerID"])
y_test = test["Churn"]

numericas = X_train.select_dtypes(include=["number"]).columns.tolist()
categoricas = X_train.select_dtypes(exclude=["number"]).columns.tolist()

def crear_preprocesador():
    return ColumnTransformer([
        ("numericas", Pipeline([
            ("imputador", SimpleImputer(strategy="median")),
            ("escalador", StandardScaler())
        ]), numericas),
        ("categoricas", Pipeline([
            ("imputador", SimpleImputer(strategy="most_frequent")),
            ("codificador", OneHotEncoder(handle_unknown="ignore"))
        ]), categoricas)
    ])

modelos = [
    ("01_Regresion_Logistica", False,
     LogisticRegression(max_iter=1000, random_state=42)),
    ("02_Regresion_Balanceada", False,
     LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)),
    ("03_Regresion_SMOTE", True,
     LogisticRegression(max_iter=1000, random_state=42)),
    ("04_Random_Forest_SMOTE", True,
     RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=1))
]

mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000"))
mlflow.set_experiment("Telco_Churn_Entrega3")

print("===== INICIO DE ENTRENAMIENTO =====", flush=True)
print("Train:", X_train.shape, "Test:", X_test.shape, flush=True)

for nombre, usar_smote, clasificador in modelos:
    print(f"\n===== {nombre} =====", flush=True)

    pasos = [("preprocesamiento", crear_preprocesador())]

    if usar_smote:
        pasos.append(("smote", SMOTE(random_state=42)))

    pasos.append(("clasificador", clasificador))

    modelo = ImbPipeline(pasos) if usar_smote else Pipeline(pasos)

    with mlflow.start_run(run_name=nombre):
        mlflow.set_tags({
            "proyecto": "Telco Customer Churn",
            "entrega": "3",
            "tipo_ejecucion": "entrenamiento_nuevo",
            "datos": "particion_estratificada_2026"
        })

        mlflow.log_params({
            "algoritmo": type(clasificador).__name__,
            "test_size": 0.2,
            "random_state": 42,
            "stratify": "Churn",
            "smote": usar_smote,
            "max_iter": getattr(clasificador, "max_iter", "No aplica"),
            "class_weight": str(getattr(clasificador, "class_weight", None)),
            "n_estimators": getattr(clasificador, "n_estimators", "No aplica")
        })

        modelo.fit(X_train, y_train)

        pred = modelo.predict(X_test)
        prob = modelo.predict_proba(X_test)[:, 1]

        metricas = {
            "Accuracy": accuracy_score(y_test, pred),
            "Precision": precision_score(y_test, pred, zero_division=0),
            "Recall": recall_score(y_test, pred, zero_division=0),
            "F1_score": f1_score(y_test, pred, zero_division=0),
            "AUC_ROC": roc_auc_score(y_test, prob)
        }

        mlflow.log_metrics(metricas)

        carpeta = BASE / "artefactos"
        carpeta.mkdir(exist_ok=True)

        matriz = confusion_matrix(y_test, pred).tolist()

        with open(carpeta / "matriz_confusion.json", "w") as f:
            json.dump({"matriz": matriz}, f, indent=2)

        joblib.dump(modelo, carpeta / "modelo.joblib")

        mlflow.log_artifacts(str(carpeta), artifact_path="evaluacion")

        print("Metricas:", metricas, flush=True)
        print("Matriz de confusion:", matriz, flush=True)
        print("Registrado en MLflow correctamente.", flush=True)

    del modelo
    gc.collect()

print("\n===== CUATRO MODELOS COMPLETADOS =====", flush=True)
