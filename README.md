# Telco Customer Churn: predicción de churn y priorización de retención

Proyecto del curso **Despliegue de Soluciones Analíticas (MIAD, Universidad de los Andes)**.
Producto de datos que estima la probabilidad de churn de cada cliente y la **pérdida esperada de MRR**, para que el área de retención priorice sus campañas. El producto se compone de un modelo supervisado, una API, un tablero y un despliegue en Docker.

- **Datos:** [Kaggle: Telco Customer Churn (IBM)](https://www.kaggle.com/datasets/blastchar/telco-customer-churn/data). 7.043 clientes y 21 variables.
- **Problema y pregunta de negocio:** [`docs/01_problema_y_preguntas_negocio.md`](docs/01_problema_y_preguntas_negocio.md)
- **Exploración de datos:** [`notebooks/01_exploracion_datos.ipynb`](notebooks/01_exploracion_datos.ipynb) (también en HTML en `reports/`)
- **Guía de Git y DVC:** [`docs/GUIA_GIT_DVC.md`](docs/GUIA_GIT_DVC.md)

## Estructura

```
telco-churn/
├── data/
│   ├── raw/                 # datos originales (versionados con DVC: *.dvc)
│   └── processed/           # salidas del pipeline (versionadas con DVC: dvc.lock)
├── docs/                    # problema, pregunta de negocio, guía Git/DVC
├── notebooks/               # exploración de datos
├── reports/figures/         # figuras para el reporte
├── src/data/
│   ├── make_dataset.py      # etapa `preparar`: limpieza y variables derivadas
│   └── split_data.py        # etapa `particion`: train/test estratificado
├── dvc.yaml                 # definición del pipeline
├── params.yaml              # parámetros (rutas, test_size, semilla)
└── requirements.txt
```

## Cómo reproducir

```bash
git clone https://github.com/<usuario>/telco-churn.git
cd telco-churn
pip install -r requirements.txt
dvc pull            # descarga los datos desde el remoto DVC
dvc repro           # regenera data/processed si algo cambió
jupyter notebook notebooks/01_exploracion_datos.ipynb
```

## Pipeline DVC

```
data/raw/WA_Fn-UseC_-Telco-Customer-Churn.csv
        │  preparar  (src/data/make_dataset.py)
        ▼
data/processed/telco_churn_limpio.csv
        │  particion (src/data/split_data.py, params: split.*)
        ▼
data/processed/train.csv · data/processed/test.csv
```

## Hallazgos principales de la exploración

| Hallazgo | Dato |
|---|---|
| Tasa de churn | 26,5 % de los clientes (desbalance 2,8 : 1) |
| MRR perdido | USD 139 mil/mes, el 30,5 % del MRR |
| Contrato mes a mes | 43 % de churn, frente a 3 % en contratos de 2 años |
| Primeros 6 meses | 53 % de churn |
| Segmento crítico | Mes a mes + fibra + cheque electrónico: 19 % de los clientes y 49 % del MRR perdido |
| Línea base | AUC ≈ 0,84. El 20 % de clientes con mayor riesgo concentra el 49 % de los churners (lift 2,5x) |
