
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


st.markdown("""
<style>
    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1500px;
    }

    .telco-header {
        background: linear-gradient(110deg, #14283F, #244C73);
        border-radius: 16px;
        padding: 28px 34px;
        margin-bottom: 18px;
    }

    .telco-eyebrow {
        color: #B7D7F2;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1.5px;
    }

    .telco-header h1 {
        color: white;
        font-size: 32px;
        line-height: 1.2;
        margin: 10px 0;
        font-weight: 700;
    }

    .telco-header p {
        color: #E0EBF5;
        font-size: 15px;
        margin: 0;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #DFE7F0;
        border-radius: 12px;
        padding: 18px 16px;
        box-shadow: 0 3px 12px rgba(20, 40, 63, 0.05);
        min-height: 125px;
    }

    div[data-testid="stMetricLabel"] {
        color: #50637B;
    }

    div[data-testid="stMetricValue"] {
        color: #14283F;
        font-weight: 700;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
    }

    .stTabs [data-baseweb="tab"] {
        padding: 12px 16px;
        font-weight: 600;
    }

    div[data-testid="stVerticalBlock"] {
        gap: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="telco-header">
    <div class="telco-eyebrow">TELCO CUSTOMER CHURN · ENTREGA 3</div>
    <h1>Inteligencia de abandono de clientes</h1>
    <p>Análisis histórico, predicción y priorización para estrategias de retención</p>
</div>
""", unsafe_allow_html=True)

with st.expander("⚙️ Ajustar filtros del análisis", expanded=False):

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


tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Resumen ejecutivo",
    "📈 Análisis histórico",
    "🤖 Predicción",
    "🎯 Priorización"
])

with tab1:
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


with tab2:
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
            margin=dict(l=10, r=75, t=60, b=20),
            xaxis_range=[0, max(55, resumen["Tasa_Churn"].max() * 1.22)],
            plot_bgcolor="white",
            paper_bgcolor="white"
        )

        return fig

    if not datos.empty:
        g1, g2, g3 = st.columns(3)

        with g1:
            st.plotly_chart(
                grafico_churn("Contract", "Abandono por contrato"),
                width="stretch"
            )

        with g2:
            st.plotly_chart(
                grafico_churn("PaymentMethod", "Abandono por método de pago"),
                width="stretch"
            )

        with g3:
            st.plotly_chart(
                grafico_churn("InternetService", "Abandono por servicio de internet"),
                width="stretch"
            )
    else:
        st.warning("No hay clientes para los filtros seleccionados.")



with tab3:
    st.subheader("Análisis predictivo de abandono")

    st.caption(
        "Predicciones del modelo de regresión logística balanceada "
        "sobre 1.409 clientes del conjunto de prueba, antes de aplicar filtros."
    )

    COLOR_RIESGO = {
        "Alto": "#D9534F",
        "Medio": "#E6A23C",
        "Bajo": "#39A58A"
    }

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
                color="Nivel_Riesgo",
                color_discrete_map=COLOR_RIESGO,
                
                category_orders={"Nivel_Riesgo": orden_riesgo}
            )

            fig_clientes.update_layout(
                title="Clientes por nivel de riesgo",
                xaxis_title="Número de clientes",
                yaxis_title="",
                height=350,
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(color="#24364B"),
                margin=dict(l=15, r=35, t=55, b=20)
            )

            st.plotly_chart(
                fig_clientes,
                width="stretch"
            )

        with p2:
            fig_mrr = px.bar(
                resumen_pred,
                x="MRR_Esperado",
                y="Nivel_Riesgo",
                orientation="h",
                text="MRR_Esperado",
                color="Nivel_Riesgo",
                color_discrete_map=COLOR_RIESGO,
                
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
                height=350,
                xaxis_range=[
                    0,
                    max(1, resumen_pred["MRR_Esperado"].max() * 1.25)
                ],
                showlegend=False,
                plot_bgcolor="white",
                paper_bgcolor="white",
                font=dict(color="#24364B"),
                margin=dict(l=15, r=35, t=55, b=20)
            )

            st.plotly_chart(
                fig_mrr,
                width="stretch"
            )

    else:
        st.warning(
            "No hay clientes con predicciones para los filtros seleccionados."
        )


    st.divider()
    from prediccion_api import mostrar_prediccion
    mostrar_prediccion()

with tab4:
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

    import plotly.graph_objects as go

    # Colores según prioridad de retención, no según cantidad
    colores_prioridad = [
        ["#E5B25B", "#A7CDB9", "#75B79C"],
        ["#D97B4E", "#E5B25B", "#A7CDB9"],
        ["#B94343", "#D97B4E", "#E5B25B"]
    ]

    # Plotly muestra las filas de abajo hacia arriba
    matriz_visual = matriz.iloc[::-1]

    fig_matriz = go.Figure()

    fig_matriz.add_trace(
        go.Heatmap(
            z=[
                [1, 0.5, 0],
                [2, 1, 0.5],
                [3, 2, 1]
            ],
            x=niveles,
            y=list(reversed(niveles)),
            colorscale=[
                [0, "#75B79C"],
                [0.33, "#E5B25B"],
                [0.66, "#D97B4E"],
                [1, "#B94343"]
            ],
            showscale=False,
            text=matriz_visual.values,
            texttemplate="%{text}",
            textfont=dict(size=18),
            hovertemplate=(
                "Impacto económico: %{x}<br>"
                "Riesgo de abandono: %{y}<br>"
                "Clientes: %{text}<extra></extra>"
            )
        )
    )

    fig_matriz.update_layout(
        title="Distribución de clientes por riesgo e impacto",
        xaxis_title="Impacto económico",
        yaxis_title="Riesgo de abandono",
        height=420,
        margin=dict(l=20, r=20, t=65, b=35),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    st.plotly_chart(fig_matriz, width="stretch")

    st.caption(
        f"Umbrales de impacto: bajo < US${p33:.2f}; "
        f"medio entre US${p33:.2f} y US${p67:.2f}; "
        f"alto desde US${p67:.2f}."
    )


    st.divider()
    st.subheader("Tabla de decisión: clientes priorizados para contacto")

    if not datos_pred.empty:
        clientes_alto_riesgo = int(
            (datos_pred["Nivel_Riesgo"] == "Alto").sum()
        )

        mrr_esperado_total = datos_pred["MRR_Esperado_Riesgo"].sum()

        clientes_prioridad_maxima = int(
            (
                (datos_pred["Nivel_Riesgo"] == "Alto")
                & (datos_pred["MonthlyCharges"] >= p67)
            ).sum()
        )

        indicador1, indicador2, indicador3 = st.columns(3)

        indicador1.metric(
            "Clientes de alto riesgo",
            f"{clientes_alto_riesgo:,}"
        )

        indicador2.metric(
            "MRR esperado en riesgo",
            f"US${mrr_esperado_total:,.2f}"
        )

        indicador3.metric(
            "Clientes de máxima prioridad",
            f"{clientes_prioridad_maxima:,}"
        )

        st.caption(
            "Máxima prioridad: riesgo alto e impacto económico alto. "
            "El MRR esperado en riesgo es una estimación, no una pérdida confirmada."
        )

        tabla = datos_pred.copy()

        tabla["Impacto_Economico"] = (
            tabla["MonthlyCharges"].apply(clasificar_impacto)
        )

        def prioridad_contacto(fila):
            riesgo = fila["Nivel_Riesgo"]
            impacto = fila["Impacto_Economico"]

            if riesgo == "Alto" and impacto == "Alto":
                return "1 - Crítica"
            if riesgo == "Alto" or (
                riesgo == "Medio" and impacto == "Alto"
            ):
                return "2 - Alta"
            return "3 - Seguimiento"

        tabla["Prioridad_Contacto"] = tabla.apply(
            prioridad_contacto, axis=1
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
                "Prioridad_Contacto",
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
                "Prioridad_Contacto": "Prioridad de contacto",
                "MRR_Esperado_Riesgo": "MRR esperado en riesgo (USD)"
            }
        )

        st.dataframe(
            tabla,
            width="stretch",
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

    # Predicción individual mediante la API desplegada
