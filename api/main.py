
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(
    title="Telco Customer Churn API",
    version="1.0.0"
)

MODEL_PATH = (
    Path(__file__).resolve().parent.parent
    / "models"
    / "regresion_balanceada.joblib"
)

modelo = joblib.load(MODEL_PATH)


class Cliente(BaseModel):
    model_config = ConfigDict(extra="forbid")

    gender: str
    SeniorCitizen: str
    Partner: str
    Dependents: str
    tenure: int = Field(ge=0)
    PhoneService: str
    MultipleLines: str
    InternetService: str
    OnlineSecurity: str
    OnlineBackup: str
    DeviceProtection: str
    TechSupport: str
    StreamingTV: str
    StreamingMovies: str
    Contract: str
    PaperlessBilling: str
    PaymentMethod: str
    MonthlyCharges: float = Field(ge=0)
    TotalCharges: float = Field(ge=0)
    tenure_grupo: str
    num_servicios: int = Field(ge=0)
    tiene_internet: str
    pago_automatico: str
    cargo_promedio_hist: float
    delta_cargo: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(cliente: Cliente):
    try:
        datos = pd.DataFrame([cliente.model_dump()])
        datos = datos[list(modelo.feature_names_in_)]

        prediccion = int(modelo.predict(datos)[0])
        probabilidad = float(
            modelo.predict_proba(datos)[0, 1]
        )

        return {
            "prediccion": prediccion,
            "probabilidad_abandono": probabilidad
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Error al generar la predicción"
        ) from error
