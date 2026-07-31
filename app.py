import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import folium

from folium.plugins import MarkerCluster, Fullscreen
from streamlit_folium import st_folium


# Configuración de la página

st.set_page_config(
    page_title="Venezuela Earthquake Analytics",
    page_icon="🌎",
    layout="wide"
)

st.markdown("""
<style>

/* Título de cada métrica */
[data-testid="stMetricLabel"] {
    font-size: 20px !important;
    font-weight: bold !important;
}

/* Valor de la métrica */
[data-testid="stMetricValue"] {
    font-size: 40px !important;
    font-weight: bold !important;
}

/* Tarjeta de la métrica */
[data-testid="stMetric"] {
    background-color: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #dcdcdc;
    text-align: center;
}

</style>
""", unsafe_allow_html=True)


st.title("🌎 Venezuela Earthquake Analytics")
st.caption("Interactive dashboard using USGS earthquake data (2000–Present)")


# Leer datos

df = pd.read_csv("data/processed/terremotos_venezuela_filtrado.csv")

df = df[df["mag"] > 0].copy()

df["time"] = pd.to_datetime(df["time"])

df["year"] = df["time"].dt.year


# Sidebar

st.sidebar.header("Filtros")

magnitud = st.sidebar.slider(
    "Magnitud mínima",
    0.0,
    float(df["mag"].max()),
    4.0
)

# Lista de años
anios = sorted(df["year"].unique(), reverse=True)

# Agregar opción "Todos"
opciones = ["Todos"] + list(anios)

anio = st.sidebar.selectbox(
    "Año",
    opciones
)

# Aplicar filtros
if anio == "Todos":
    df_filtrado = df[
        df["mag"] >= magnitud
    ]
else:
    df_filtrado = df[
        (df["year"] == anio) &
        (df["mag"] >= magnitud)
    ]


# Verificar si hay datos
if df_filtrado.empty:
    st.warning("No hay terremotos para los filtros seleccionados.")
    st.stop()

st.divider()
# Estadísticas

st.subheader("📊 Estadísticas")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "🌋 Eventos",
        len(df_filtrado)
    )

with col2:
    st.metric(
    "📈 Magnitud máxima",
    round(df_filtrado["mag"].max(), 1)
)

with col3:
    st.metric(
    "📉 Magnitud promedio",
    round(df_filtrado["mag"].mean(), 2)
)

with col4:
    st.metric(
    "📏 Profundidad promedio",
    round(df_filtrado["depth"].mean(), 2)
)

with col5:
    ultimo = df_filtrado["time"].max()

    st.metric(
        "📅 Último evento",
        ultimo.strftime("%d/%m/%Y")
)

st.divider()
# Layout principal
col_mapa, col_grafico = st.columns([2.7, 1])

# ---------------- MAPA ----------------

with col_mapa:

    st.subheader("🗺️ Mapa interactivo")

    mapa = folium.Map(
        location=[8.5, -66],
        zoom_start=6,
        tiles="OpenStreetMap"
    )

    Fullscreen().add_to(mapa)

    cluster = MarkerCluster().add_to(mapa)

    for _, fila in df_filtrado.iterrows():

        if fila["mag"] >= 6:
            color = "red"
        elif fila["mag"] >= 5:
            color = "orange"
        else:
            color = "blue"

        folium.CircleMarker(

            location=[fila["latitude"], fila["longitude"]],

            radius=max(fila["mag"] * 0.6, 2),

            color=color,

            fill=True,

            fill_color=color,

            fill_opacity=0.7,

            weight=1,

            tooltip=f"{fila['place']} (M {fila['mag']})",

            popup=folium.Popup(
                f"""
                <b>📍 Lugar:</b> {fila['place']}<br>
                <b>📈 Magnitud:</b> {fila['mag']}<br>
                <b>📏 Profundidad:</b> {fila['depth']} km<br>
                <b>📅 Fecha:</b> {fila['time'].strftime('%d/%m/%Y')}
                """,
                max_width=300
            )

        ).add_to(cluster)

    legend_html = """
    <div style="
    position: fixed;
    bottom:40px;
    left:40px;
    width:200px;
    background:white;
    border-radius:10px;
    padding:10px;
    box-shadow:0 0 10px rgba(0,0,0,.3);
    z-index:9999;
    ">

    <b>Magnitud</b><br><br>

    🔴 ≥ 6<br>
    🟠 5 - 5.9<br>
    🔵 < 5

    </div>
    """

    mapa.get_root().html.add_child(
        folium.Element(legend_html)
    )

    st_folium(
        mapa,
        width=None,
        height=520
    )

# ---------------- HISTOGRAMA ----------------

with col_grafico:

    st.subheader("📊 Distribución")

    st.write("")
    st.write("")
    st.write("")
    st.write("")

    fig, ax = plt.subplots(figsize=(4.5,3.5))

    ax.hist(
        df_filtrado["mag"],
        bins=15,
        edgecolor="black",
        color="steelblue"
    )

    ax.set_xlabel("Magnitud")
    ax.set_ylabel("Eventos")

    plt.tight_layout()

    st.pyplot(fig)

st.divider()

st.subheader("🏆 Top 10 terremotos más fuertes")

top10 = (
    df_filtrado[
        ["time", "place", "mag", "depth"]
    ]
    .sort_values("mag", ascending=False)
    .head(10)
    .rename(columns={
        "time": "Fecha",
        "place": "Ubicación",
        "mag": "Magnitud",
        "depth": "Profundidad (km)"
    })
)

top10["Fecha"] = pd.to_datetime(
    top10["Fecha"]
).dt.strftime("%d/%m/%Y")

st.dataframe(
    top10,
    use_container_width=True
)

st.divider()
st.subheader("📈 Eventos por año")

eventos = (
    df_filtrado
    .groupby("year")
    .size()
)

st.bar_chart(eventos)