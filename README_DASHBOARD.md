# Dashboard de abandono de clientes — Entrega 2

## Descripción
Dashboard interactivo desarrollado con Streamlit para analizar
el abandono histórico y el riesgo predictivo de los clientes.

## Requisitos
- Python 3.10 o superior.
- Dataset original Telco Customer Churn.

## 1. Instalar dependencias

    pip install -r requirements.txt

## 2. Preparar los datos

Ubicar el CSV original en:

    data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv

Ejecutar desde la raíz del repositorio:

    python src/data/make_dataset.py

Se generará el archivo:

    data/processed/telco_churn_limpio.csv

## 3. Datos predictivos

Las predicciones están disponibles en:

    reports/dashboard/predicciones_churn.csv

Corresponden a 1.409 clientes del conjunto de prueba.

## 4. Ejecutar el dashboard

    streamlit run app.py

## 5. Funcionalidades
- Filtros interactivos por contrato, pago, internet y antigüedad.
- Cinco indicadores históricos de abandono.
- Gráficos de churn por segmento.
- Clientes clasificados por nivel de riesgo.
- MRR esperado en riesgo.
- Matriz de riesgo e impacto económico.
- Tabla de clientes priorizados y descarga CSV.

## Consideraciones
Los indicadores históricos utilizan 7.043 clientes.
Las predicciones corresponden a 1.409 clientes de prueba.
El MRR esperado en riesgo es una estimación, no una pérdida confirmada.
Los niveles de riesgo utilizan umbrales operativos propuestos.
Los valores monetarios corresponden a USD.
