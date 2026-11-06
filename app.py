
import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="Dashboard Telco Churn",
    page_icon="📊",
    layout="wide"
)

BASE = Path(__file__).resolve().parent

@st.cache_data
def cargar_datos():
    historico = pd.read_csv(
        BASE / "data/processed/telco_churn_limpio.csv"
    )
    predicciones = pd.read_csv(
        BASE / "reports/dashboard/predicciones_churn.csv"
    )
    return historico, predicciones

historico, predicciones = cargar_datos()

st.title("📊 Panel de Análisis de Abandono de Clientes")
st.caption("Proyecto Telco Customer Churn | Entrega 2")

st.subheader("Filtros")

c1, c2, c3, c4 = st.columns(4)

with c1:
    contratos = st.multiselect(
        "Tipo de contrato",
        sorted(historico["Contract"].dropna().unique()),
        default=sorted(historico["Contract"].dropna().unique())
    )

with c2:
    pagos = st.multiselect(
        "Método de pago",
        sorted(historico["PaymentMethod"].dropna().unique()),
        default=sorted(historico["PaymentMethod"].dropna().unique())
    )

with c3:
    internet = st.multiselect(
        "Servicio de internet",
        sorted(historico["InternetService"].dropna().unique()),
        default=sorted(historico["InternetService"].dropna().unique())
    )

with c4:
    antiguedad = st.slider(
        "Antigüedad (meses)",
        min_value=0,
        max_value=72,
        value=(0, 72)
    )

def filtrar(df):
    return df[
        df["Contract"].isin(contratos)
        & df["PaymentMethod"].isin(pagos)
        & df["InternetService"].isin(internet)
        & df["tenure"].between(*antiguedad)
    ]

datos = filtrar(historico)
datos_pred = filtrar(predicciones)

st.divider()
st.subheader("Indicadores generales")

total = len(datos)
abandonaron = int(datos["Churn"].sum())
tasa = abandonaron / total if total else 0
cargo_promedio = datos["MonthlyCharges"].mean() if total else 0
mrr_perdido = datos.loc[
    datos["Churn"] == 1, "MonthlyCharges"
].sum()

k1, k2, k3, k4, k5 = st.columns(5)

k1.metric("Total de clientes", f"{total:,}")
k2.metric("Clientes que abandonaron", f"{abandonaron:,}")
k3.metric("Tasa histórica de churn", f"{tasa:.1%}")
k4.metric("Cargo mensual promedio", f"${cargo_promedio:,.2f}")
k5.metric("MRR histórico perdido", f"${mrr_perdido:,.2f}")

st.divider()
st.info(
    "Los indicadores superiores corresponden al conjunto histórico. "
    "La sección predictiva utilizará los clientes del conjunto de prueba."
)

st.write(
    f"Clientes disponibles para análisis predictivo: {len(datos_pred):,}"
)


import plotly.express as px

st.divider()
st.subheader("Análisis histórico de abandono")

def grafico_churn(columna, titulo):
    resumen = (
        datos.groupby(columna, as_index=False)
        .agg(
            Clientes=("Churn", "count"),
            Tasa_Churn=("Churn", "mean")
        )
    )

    resumen["Tasa_Churn"] *= 100

    fig = px.bar(
        resumen.sort_values("Tasa_Churn"),
        x="Tasa_Churn",
        y=columna,
        orientation="h",
        text="Tasa_Churn",
        color_discrete_sequence=["#287DB8"]
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside"
    )

    fig.update_layout(
        title=titulo,
        xaxis_title="Tasa de abandono (%)",
        yaxis_title="",
        height=360,
        margin=dict(l=10, r=35, t=60, b=20)
    )

    return fig

if not datos.empty:
    g1, g2, g3 = st.columns(3)

    with g1:
        st.plotly_chart(
            grafico_churn("Contract", "Abandono por contrato"),
            use_container_width=True
        )

    with g2:
        st.plotly_chart(
            grafico_churn("PaymentMethod", "Abandono por método de pago"),
            use_container_width=True
        )

    with g3:
        st.plotly_chart(
            grafico_churn("InternetService", "Abandono por servicio de internet"),
            use_container_width=True
        )
else:
    st.warning("No hay clientes para los filtros seleccionados.")


st.divider()
st.subheader("Análisis predictivo de abandono")

st.caption(
    "Predicciones del modelo de regresión logística balanceada "
    "sobre 1.409 clientes del conjunto de prueba, antes de aplicar filtros."
)

orden_riesgo = ["Alto", "Medio", "Bajo"]

if not datos_pred.empty:
    resumen_pred = (
        datos_pred.groupby("Nivel_Riesgo")
        .agg(
            Clientes=("customerID", "count"),
            MRR_Expuesto=("MonthlyCharges", "sum"),
            MRR_Esperado=("MRR_Esperado_Riesgo", "sum")
        )
        .reindex(orden_riesgo, fill_value=0)
        .reset_index()
    )

    p1, p2 = st.columns(2)

    with p1:
        fig_clientes = px.bar(
            resumen_pred,
            x="Clientes",
            y="Nivel_Riesgo",
            orientation="h",
            text="Clientes",
            color_discrete_sequence=["#287DB8"],
            category_orders={"Nivel_Riesgo": orden_riesgo}
        )

        fig_clientes.update_layout(
            title="Clientes por nivel de riesgo",
            xaxis_title="Número de clientes",
            yaxis_title="",
            height=350
        )

        st.plotly_chart(
            fig_clientes,
            use_container_width=True
        )

    with p2:
        fig_mrr = px.bar(
            resumen_pred,
            x="MRR_Esperado",
            y="Nivel_Riesgo",
            orientation="h",
            text="MRR_Esperado",
            color_discrete_sequence=["#287DB8"],
            category_orders={"Nivel_Riesgo": orden_riesgo}
        )

        fig_mrr.update_traces(
            texttemplate="$%{text:,.0f}",
            textposition="outside"
        )

        fig_mrr.update_layout(
            title="MRR esperado en riesgo por nivel (USD)",
            xaxis_title="MRR esperado en riesgo (USD)",
            yaxis_title="",
            height=350
        )

        st.plotly_chart(
            fig_mrr,
            use_container_width=True
        )

else:
    st.warning(
        "No hay clientes con predicciones para los filtros seleccionados."
    )


st.divider()
st.subheader("Segmentos prioritarios para retención")

st.caption(
    "Matriz de clientes por riesgo de abandono e impacto económico. "
    "El impacto se clasifica según los percentiles 33 y 67 "
    "del cargo mensual del conjunto de prueba."
)

# Umbrales calculados sobre el conjunto de prueba completo
p33 = predicciones["MonthlyCharges"].quantile(0.33)
p67 = predicciones["MonthlyCharges"].quantile(0.67)

def clasificar_impacto(cargo):
    if cargo >= p67:
        return "Alto"
    elif cargo >= p33:
        return "Medio"
    return "Bajo"

datos_matriz = datos_pred.copy()

datos_matriz["Impacto_Economico"] = (
    datos_matriz["MonthlyCharges"].apply(clasificar_impacto)
)

niveles = ["Alto", "Medio", "Bajo"]

matriz = pd.crosstab(
    datos_matriz["Nivel_Riesgo"],
    datos_matriz["Impacto_Economico"]
).reindex(index=niveles, columns=niveles, fill_value=0)

fig_matriz = px.imshow(
    matriz,
    text_auto=True,
    color_continuous_scale="Purples",
    labels={
        "x": "Impacto económico",
        "y": "Riesgo de abandono",
        "color": "Clientes"
    },
    aspect="auto"
)

fig_matriz.update_layout(
    height=400,
    xaxis_title="Impacto económico",
    yaxis_title="Riesgo de abandono"
)

st.plotly_chart(fig_matriz, use_container_width=True)

st.caption(
    f"Umbrales de impacto: bajo < US${p33:.2f}; "
    f"medio entre US${p33:.2f} y US${p67:.2f}; "
    f"alto desde US${p67:.2f}."
)


st.divider()
st.subheader("Tabla de decisión: clientes priorizados para contacto")

if not datos_pred.empty:
    tabla = datos_pred.copy()

    tabla["Impacto_Economico"] = (
        tabla["MonthlyCharges"].apply(clasificar_impacto)
    )

    tabla = tabla.sort_values(
        "MRR_Esperado_Riesgo",
        ascending=False
    )

    tabla = tabla[
        [
            "customerID",
            "tenure",
            "Contract",
            "InternetService",
            "PaymentMethod",
            "MonthlyCharges",
            "Probabilidad_Churn",
            "Nivel_Riesgo",
            "Impacto_Economico",
            "MRR_Esperado_Riesgo"
        ]
    ].rename(
        columns={
            "customerID": "ID de cliente",
            "tenure": "Antigüedad (meses)",
            "Contract": "Tipo de contrato",
            "InternetService": "Servicio de internet",
            "PaymentMethod": "Método de pago",
            "MonthlyCharges": "Cargo mensual (USD)",
            "Probabilidad_Churn": "Probabilidad de abandono",
            "Nivel_Riesgo": "Nivel de riesgo",
            "Impacto_Economico": "Impacto económico",
            "MRR_Esperado_Riesgo": "MRR esperado en riesgo (USD)"
        }
    )

    st.dataframe(
        tabla,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Probabilidad de abandono": st.column_config.ProgressColumn(
                "Probabilidad de abandono",
                min_value=0,
                max_value=1,
                format="percent"
            ),
            "Cargo mensual (USD)": st.column_config.NumberColumn(
                "Cargo mensual (USD)",
                format="$%.2f"
            ),
            "MRR esperado en riesgo (USD)": st.column_config.NumberColumn(
                "MRR esperado en riesgo (USD)",
                format="$%.2f"
            )
        }
    )

    st.download_button(
        label="Descargar clientes priorizados (CSV)",
        data=tabla.to_csv(index=False).encode("utf-8-sig"),
        file_name="clientes_priorizados_churn.csv",
        mime="text/csv"
    )

    st.caption(
        f"Se muestran {len(tabla):,} clientes del conjunto de prueba, "
        "ordenados por MRR esperado en riesgo. "
        "La priorización es orientativa y no garantiza el abandono."
    )
else:
    st.warning(
        "No hay clientes para mostrar con los filtros seleccionados."
    )
