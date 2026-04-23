import streamlit as st
import pandas as pd
import plotly.express as px
import os
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Caja Complementaria FRAY MAMERTO ESQUIU", layout="wide")

st.title("📊 Dashboard Caja Complementaria FME - Datos hasta Marzo 2026")

# =========================
# DATA
# =========================

df = pd.read_csv("datos.csv")
df["fecha"] = pd.to_datetime(df["periodo"])
df["recaudacion"] = df["masa_salarial"] * 0.05

# =========================
# KPIs
# =========================

total = df["recaudacion"].sum()
ultimo_valor = df.iloc[-1]["recaudacion"]

def formato(x):
    return f"${x:,.0f}".replace(",", ".")

col1, col2 = st.columns(2)
col1.metric("💰 Total Recaudación al 5%", formato(total))
col2.metric("📅 Último valor recaudado de Marzo 2026", formato(ultimo_valor))

# =========================
# GRÁFICO
# =========================

fig = px.line(df, x="fecha", y="recaudacion", markers=True)
fig.update_layout(
    yaxis_title="Recaudación 5%",
    xaxis_title="Periodo"
)

st.plotly_chart(fig, use_container_width=True)

# =========================
# TABLA ANUAL
# =========================

# =========================
# TABLA ANUAL + TOTAL
# =========================

tabla_anual = df.groupby(df["fecha"].dt.year).agg({
    "masa_salarial": "sum",
    "recaudacion": "sum"
}).reset_index()

# Crear fila TOTAL
total_row = pd.DataFrame({
    "fecha": ["TOTAL"],
    "masa_salarial": [tabla_anual["masa_salarial"].sum()],
    "recaudacion": [tabla_anual["recaudacion"].sum()]
})

# Unir
tabla_anual = pd.concat([tabla_anual, total_row], ignore_index=True)

# Renombrar columnas
tabla_anual = tabla_anual.rename(columns={
    "fecha": "Año",
    "masa_salarial": "Remuneración Total",
    "recaudacion": "Recaudación 5%"
})

# Formato miles
def formato(x):
    return f"${x:,.0f}".replace(",", ".")

tabla_anual["Remuneración Total"] = tabla_anual["Remuneración Total"].apply(
    lambda x: formato(x) if isinstance(x, (int, float)) else x
)

tabla_anual["Recaudación 5%"] = tabla_anual["Recaudación 5%"].apply(
    lambda x: formato(x) if isinstance(x, (int, float)) else x
)

st.subheader("📋 Resumen anual")
st.dataframe(tabla_anual, use_container_width=True)

st.subheader("⚖️ Punto de equilibrio")


#CALCULO PARA EQUILIBROP

activos = 742
masa_salarial = 667698233.6
recaudacion = masa_salarial * 0.05
haber_promedio = 284733.75

equilibrio = recaudacion / haber_promedio

jubilados = np.arange(0, 300, 10)
erogacion = jubilados * haber_promedio
print(erogacion)

# pasar a millones
recaudacion_millones = recaudacion / 1_000_000
erogacion_millones = erogacion / 1_000_000

fig_eq = go.Figure()

# línea erogación
fig_eq.add_trace(go.Scatter(
    x=jubilados,
    y=erogacion_millones,
    mode='lines',
    name='Erogación (Pasivos)'
))

# línea recaudación
fig_eq.add_hline(
    y=recaudacion_millones,
    line_dash="dash",
    annotation_text="Recaudación (Activos)"
)

# punto equilibrio
fig_eq.add_trace(go.Scatter(
    x=[equilibrio],
    y=[recaudacion_millones],
    mode='markers+text',
    text=[f"{equilibrio:.0f} jubilados"],
    textposition="top center",
    name="Equilibrio"
))

fig_eq.update_layout(
    title=f"Punto de equilibrio con {activos} agentes activos",
    xaxis_title="Cantidad de jubilados",
    yaxis_title="Monto (millones $)"
)

st.plotly_chart(fig_eq, use_container_width=True)

st.subheader("📈 Equilibrio según porcentaje de aporte")

porcentajes = np.linspace(0.01, 0.15, 50)
jubilados_equilibrio = (masa_salarial * porcentajes) / haber_promedio
porcentajes_pct = porcentajes * 100

fig_pct = go.Figure()

# línea principal
fig_pct.add_trace(go.Scatter(
    x=porcentajes_pct,
    y=jubilados_equilibrio,
    mode='lines',
    name='Capacidad del sistema'
))

# punto actual 5%
fig_pct.add_trace(go.Scatter(
    x=[5],
    y=[(masa_salarial * 0.05) / haber_promedio],
    mode='markers+text',
    text=["5%"],
    textposition="top center",
    name="Situación actual"
))

# punto equilibrio real
porc_necesario = (142 * haber_promedio) / masa_salarial * 100

fig_pct.add_trace(go.Scatter(
    x=[porc_necesario],
    y=[142],
    mode='markers+text',
    text=[f"{porc_necesario:.1f}%"],
    textposition="top center",
    name="Equilibrio real"
))

fig_pct.update_layout(
    title="Estimacion de equilibrio según porcentaje de aporte",
    xaxis_title="Porcentaje de aporte (%)",
    yaxis_title="Jubilados sostenibles"
)

st.plotly_chart(fig_pct, use_container_width=True)

st.info("El sistema previsional de FME actualmente registra 142 agentes, pero solamente 135 ex-agentes perciben valores entre $ 800.000 y $ 1.200.000, promediando $ 284.733,75 y tuvieron en Marzo 2026 una erogacion total mensual de $ 23.309.818,19. La recaudación por los Activos (Aportes 2% y Contribiciones del 3%) fue de $ 33.384.912 financia el 70% de las Asig. Complementarias de los jubilados.")

st.markdown("""
### 📌 Análisis

Se observa que la recaudación actual resulta insuficiente para cubrir las erogaciones proyectadas, 
requiriéndose un incremento en la alícuota de aporte + contribucion del 5% al 6.1% para el punto de equilibrio.
Ademas, las Recaudación Total estimada del municipio desde Julio 2016 hasta Marzo 2026 fue de $830.940.075. No se encontraron datos desde 2013 a Junio 2016
""")

st.title("📊 Proyección de Jubilaciones")

# ---- Cargar datos ----

ruta = os.path.join(os.path.dirname(__file__), "fme.xlsx")

print(ruta)  # para debug

df = pd.read_excel(ruta)
df = pd.read_excel("fme.xlsx")

# MOCK para probar si querés
# df = pd.DataFrame({
#     "sexo": ["F","M","F","M"],
#     "EDAD": [58, 63, 59, 64]
# })

# ---- Lógica ----
df["edad_jubilatoria"] = df["sexo"].map({"F": 60, "M": 65})
df["años_para_jubilarse"] = df["edad_jubilatoria"] - df["EDAD"]

df_proj = df[
    (df["años_para_jubilarse"] >= 0) &
    (df["años_para_jubilarse"] <= 5)
].copy()

año_actual = 2026
df_proj["año_jubilacion"] = año_actual + df_proj["años_para_jubilarse"]

proyeccion = df_proj.groupby("año_jubilacion").size().reset_index(name="cantidad")

# ---- Gráfico ----
fig = px.line(
    proyeccion,
    x="año_jubilacion",
    y="cantidad",
    markers=True,
    title="Proyección de Jubilaciones a 5 años"
)

st.plotly_chart(fig, use_container_width=True)