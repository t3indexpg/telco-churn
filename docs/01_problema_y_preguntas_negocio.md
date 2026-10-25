# Problema, pregunta de negocio y alcance

**Proyecto:** Predicción de churn y priorización de retención · Telco Customer Churn
**Datos:** [Kaggle — Telco Customer Churn (IBM)](https://www.kaggle.com/datasets/blastchar/telco-customer-churn/data)

---

## 1. Contexto

En telecomunicaciones el cliente puede cambiar de operador con poca fricción, sobre todo con contratos mes a mes. Retener a un cliente cuesta mucho menos que conseguir uno nuevo: adquirirlo puede ser entre 5 y 25 veces más costoso que retenerlo (Gallo, *Harvard Business Review*, 2014). Por eso la tasa de cancelación (*churn*) es uno de los indicadores que más pesan en el valor de una operadora.

El dataset describe a 7.043 clientes de una operadora ficticia de California (IBM) que ofrece telefonía e internet. Incluye su perfil, los servicios que tiene contratados, el tipo de contrato, la facturación y si canceló el servicio en el último mes.

**Cifras de la exploración (notebook `01_exploracion_datos.ipynb`):**

| Indicador | Valor |
|---|---|
| Tasa de churn | **26,5 %** (1.869 clientes) |
| MRR perdido por churn | **USD 139 mil/mes (30,5 % del MRR)**, ≈ USD 1,67 M anuales |
| Churn en contrato mes a mes | 43 % (vs. 3 % en contrato a 2 años) |
| Churn en los primeros 6 meses | 53 % (vs. 10 % después de 4 años) |
| Segmento mes a mes + fibra + cheque electrónico | 19 % de los clientes, 60 % de churn, **49 % del MRR perdido** |
| Poder predictivo preliminar | AUC ≈ 0,84; recall ≈ 79 % con balanceo |

---

## 2. Planteamiento del problema

> La operadora pierde cada mes al **26,5 % de sus clientes**, lo que equivale al **30,5 % de su ingreso mensual recurrente (≈ USD 1,67 M al año)**. Reponer ese ingreso con clientes nuevos cuesta varias veces más que retener a los actuales. Hoy el área de retención actúa de forma **reactiva** y, con una capacidad de contacto limitada, no tiene un criterio objetivo para decidir a quién intervenir ni con qué oferta. Los datos muestran que el riesgo se concentra en perfiles identificables: contrato mes a mes, fibra óptica, pago con cheque electrónico y menos de un año de antigüedad. Un segmento con el 19 % de los clientes explica casi la mitad del MRR perdido. El proyecto propone un **modelo supervisado de clasificación** que estime la probabilidad de churn de cada cliente y, multiplicada por su MRR, la **pérdida esperada**, para priorizar las campañas de retención donde más valor protegen. El modelo se servirá mediante una **API** y se usará desde un **tablero** que muestre el riesgo, sus factores explicativos y el impacto de las palancas de retención, desplegado en **Docker**. El modelo debe privilegiar la detección de clientes en riesgo (recall ≥ 75 %, AUC ≥ 0,80) y concentrar al menos el doble de churners que el azar en el 20 % de mayor riesgo.

---

## 3. Pregunta de negocio

### Pregunta principal
> **¿Qué clientes tienen mayor probabilidad de cancelar el servicio y cuánto ingreso mensual está en riesgo por cada uno, para que el área de retención priorice a quién contactar y con qué palanca, dentro de su capacidad de contacto?**

### Preguntas secundarias

| # | Pregunta | Tipo | Se responde con | Evidencia inicial (EDA) |
|---|---|---|---|---|
| P1 | ¿Cuál es la tasa de churn y cuánto MRR representa? | Descriptiva | Tablero (KPIs) | 26,5 % de clientes; 30,5 % del MRR |
| P2 | ¿Qué segmentos (contrato, internet, medio de pago, antigüedad) concentran el churn y el MRR perdido? | Descriptiva | Tablero (filtros, mapa de calor) | Mes a mes + fibra: 55 % churn, 72 % del MRR perdido |
| P3 | ¿En qué momento del ciclo de vida es más probable que un cliente se vaya? | Descriptiva | Tablero (curva por antigüedad) | 53 % en 0-6 meses; ventana crítica de 12 meses |
| P4 | ¿Cuál es la probabilidad de churn de un cliente dado? | Predictiva | Modelo + API | AUC preliminar 0,84 |
| P5 | ¿Qué variables explican el riesgo de cada cliente? | Predictiva / explicativa | Modelo (importancias / coeficientes) en el tablero | Contract, tenure, InternetService, PaymentMethod |
| P6 | Si se contacta al k % de mayor riesgo, ¿qué porcentaje de churners y de MRR en riesgo se cubre? | Predictiva / valor | Modelo + tablero (curva de ganancia) | Top 20 % → 49 % de churners, 54 % del MRR |
| P7 | ¿Cuánto bajaría el riesgo de un cliente si migra a contrato anual, pago automático o agrega soporte técnico? | Prescriptiva (*what-if*) | API + simulador en el tablero | 43 %→11 %, 35 %→16 %, 31 %→15 % |
| P8 | ¿Qué umbral de probabilidad conviene, dado el costo de la campaña y el valor del cliente? | Prescriptiva | Tablero (parámetro de costo) | FN más costoso que FP |


---

## 4. Alcance del proyecto

**Incluye**
- Exploración, limpieza y preparación de datos versionados (Git + DVC, pipeline `dvc repro`).
- Modelo supervisado de **clasificación binaria** (churn sí/no): comparar regresión logística, Random Forest y Gradient Boosting, con manejo del desbalance (`class_weight` / SMOTE en train) y selección por recall, F1, AUC y lift.
- Cálculo de **pérdida esperada** por cliente (probabilidad × MonthlyCharges).
- **API** (p. ej., FastAPI) que recibe los atributos de un cliente y devuelve la probabilidad, la pérdida esperada y los principales factores de riesgo.
- **Tablero** (p. ej., Dash) con: KPIs, segmentación, curva por antigüedad, ranking de clientes priorizados, curva de ganancia y simulador *what-if* conectado a la API.
- Empaquetado y despliegue en **Docker**.

**No incluye**
- Diseño ni ejecución real de campañas de retención, ni medición causal de su efecto (requeriría experimentos A/B).
- Modelos de supervivencia o de tiempo hasta el churn (el dataset es una foto, no una serie temporal).
- Integración con sistemas reales de CRM/facturación ni actualización automática de datos.
- Estimación de CLV completo (no hay margen ni costos por cliente).

**Supuestos y limitaciones**
- Datos **ficticios** de IBM: los hallazgos ilustran la metodología, no una operadora real.
- `Churn` refleja cancelaciones del último mes; se asume que los patrones se mantienen en el siguiente período.
- Cifras en **USD** (moneda original del dataset).
- El costo de contacto y la tasa de éxito de la retención no están en los datos; se tratarán como **parámetros ajustables** en el tablero.

---

## 5. Conjunto de datos a emplear

| Atributo | Detalle |
|---|---|
| Fuente | Kaggle `blastchar/telco-customer-churn` (IBM Sample Data Sets) |
| Archivo | `WA_Fn-UseC_-Telco-Customer-Churn.csv` (≈ 950 KB) |
| Registros / variables | 7.043 clientes × 21 variables (20 predictoras + `Churn`) |
| Grupos de variables | Demográficas (4), cuenta (4), servicios (9), facturación (2), llave (1), objetivo (1) |
| Calidad | Sin duplicados; 11 faltantes ocultos en `TotalCharges` (tenure = 0) imputados con 0 |
| Versionamiento | `data/raw` → `dvc add`; `data/processed` → salidas del pipeline `dvc.yaml` |
| Disponibilidad | Pública e inmediata (licencia de uso de Kaggle) |

---

## 6. Usuario y uso esperado

- **Usuario principal:** líder y analistas del área de retención / CX.
- **Uso:** cada ciclo de facturación, revisar en el tablero el ranking de clientes por pérdida esperada, filtrar por segmento, exportar la lista a contactar y usar el simulador para elegir la oferta (contrato anual, pago automático, soporte técnico).
- **Usuario secundario:** gerencia comercial/financiera, que sigue los indicadores de MRR en riesgo y el retorno de las campañas.
