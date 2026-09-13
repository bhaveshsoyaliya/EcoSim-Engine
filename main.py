
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os

from streamlit_folium import st_folium

# ===============================
# IMPORT MODULES
# ===============================

from api.weather_api import get_live_environment

from models.air_model import calculate_aqi
from models.water_model import calculate_wqi
from models.carbon_model import calculate_carbon

from simulation.forecast import forecast_pm25
from simulation.dispersion import gaussian_plume

from satellite.cdse_api import download_sentinel
from satellite.ndvi import calculate_ndvi
from satellite.raster_utils import grid_statistics

from gis.tree_planner import calculate_tree_requirement
from gis.pollution_map import create_tree_heatmap

from gis.ndvi_overlay import create_ndvi_overlay
from features.microclimate_engine import simulate_microclimate
from visualization.microclimate_chart import microclimate_heatmap
from features.tree_species_ai import recommend_species

from visualization.charts import (
    pollution_chart,
    forecast_chart,
    plume_heatmap,
    carbon_gauge
)

# ===============================
# PAGE CONFIG
# ===============================

st.set_page_config(
    page_title="EcoSim Engine",
    page_icon="🌍",
    layout="wide"
)

# ===============================
# DATABASE
# ===============================

os.makedirs("data", exist_ok=True)

CSV = "data/historical.csv"

if not os.path.exists(CSV):
    pd.DataFrame(columns=[
        "City",
        "PM2.5",
        "PM10",
        "NO2",
        "O3",
        "Temperature",
        "Humidity",
        "Wind",
        "Rain"
    ]).to_csv(CSV, index=False)

def save_history(city, d):

    columns = [
        "City", "PM2.5", "PM10", "NO2", "O3",
        "Temperature", "Humidity", "Wind", "Rain"
    ]

    # Create new DataFrame if file is missing OR empty
    if (not os.path.exists(CSV)) or os.path.getsize(CSV) == 0:
        old = pd.DataFrame(columns=columns)
    else:
        old = pd.read_csv(CSV)

    new = pd.DataFrame([{
        "City": city,
        "PM2.5": d["pm25"],
        "PM10": d["pm10"],
        "NO2": d["no2"],
        "O3": d["o3"],
        "Temperature": d["temperature"],
        "Humidity": d["humidity"],
        "Wind": d["wind"],
        "Rain": d["rain"]
    }])

    pd.concat([old, new], ignore_index=True).to_csv(CSV, index=False)

# ===============================
# AQI GAUGE
# ===============================

def create_gauge(value):

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": "PM 2.5 AQI"},
        gauge={
            "axis": {"range": [0, 300]},
            "steps": [
                {"range": [0, 50], "color": "green"},
                {"range": [50, 100], "color": "yellow"},
                {"range": [100, 200], "color": "orange"},
                {"range": [200, 300], "color": "red"}
            ]
        }
    ))

    fig.update_layout(height=300)

    return fig

# ===============================
# SIDEBAR
# ===============================

st.sidebar.title("🌍 EcoSim Engine")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Tree Planner",
        "GIS Map",
        "Forecast",
        "Dispersion",
        "Water Quality",
        "Carbon Simulator",
        "Micro-Climate Engine",
        "AI Tree Species",
        "Historical Data"
    ]
)

city = st.sidebar.text_input(
    "Enter City",
    "Ahmedabad"
)

# ===============================
# LIVE ENVIRONMENT DATA
# ===============================

data = get_live_environment(city)

if data is None:
    st.error("Unable to fetch environmental data.")
    st.stop()

save_history(city, data)

pm25 = data["pm25"]
pm10 = data["pm10"]
no2 = data["no2"]
o3 = data["o3"]

status, color = calculate_aqi(pm25, pm10)

# ===============================
# DASHBOARD PAGE
# ===============================

if page == "Dashboard":

    st.title("🌍 EcoSim Environmental Dashboard")

    if status == "GOOD":
        st.success("🟢 GOOD AIR QUALITY")

    elif status == "MODERATE":
        st.warning("🟡 MODERATE AIR QUALITY")

    else:
        st.error("🔴 UNHEALTHY AIR QUALITY")

    st.divider()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("PM 2.5", f"{pm25:.1f}")
    c2.metric("PM10", f"{pm10:.1f}")
    c3.metric("NO₂", f"{no2:.1f}")
    c4.metric("O₃", f"{o3:.1f}")

    st.divider()

    st.subheader("🌦 Live Weather")

    w1, w2, w3, w4 = st.columns(4)

    w1.metric("Temperature", f"{data['temperature']} °C")
    w2.metric("Humidity", f"{data['humidity']} %")
    w3.metric("Wind", f"{data['wind']} km/h")
    w4.metric("Rain", f"{data['rain']} mm")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.plotly_chart(
            create_gauge(pm25),
            use_container_width=True
        )

    with right:
        st.plotly_chart(
            pollution_chart(
                pm25,
                pm10,
                no2,
                o3
            ),
            use_container_width=True
        )

    st.divider()

    st.subheader("📍 Live Location")

    info1, info2 = st.columns(2)

    info1.metric("Latitude", f"{data['lat']:.4f}")
    info2.metric("Longitude", f"{data['lon']:.4f}")

    st.info(
        f"Current environmental analysis for {city} is updated automatically using live weather and pollution data."
    )

# ========= CONTINUE PART 2 =========

# ==========================================
# TREE PLANNER
# ==========================================

elif page == "Tree Planner":

    st.title("🌳 Real-Time Tree Plantation Planner")

    with st.spinner("Downloading latest Sentinel-2 image..."):
        sat = download_sentinel(
            data["lat"],
            data["lon"]
        )

    if sat is None:
        st.error("No Sentinel image found")
        st.stop()

    ds = sat["dataset"]
    ndvi = calculate_ndvi(ds)

    m = create_ndvi_overlay(ds)

    stats = grid_statistics(ndvi)

    result = calculate_tree_requirement(
        stats,
        pm25
    )

    df = pd.DataFrame(result)

    st_folium(
        m,
        width=1200,
        height=700
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "🌳 Trees Required",
        int(df["Trees Needed"].sum())
    )

    c2.metric(
        "🌿 Green Cover",
        f"{df['Vegetation %'].mean():.1f}%"
    )

    c3.metric(
        "🔴 Critical Zones",
        int((df["Priority"] == "Critical").sum())
    )

    st.divider()

    st.subheader("Grid Analysis")

    st.dataframe(
        df,
        use_container_width=True
    )

# ==========================================
# GIS MAP
# ==========================================

elif page == "GIS Map":

    st.title("🛰 Real Satellite NDVI GIS")

    sat = download_sentinel(
        data["lat"],
        data["lon"]
    )

    if sat is None:
        st.error("No Sentinel image found")
        st.stop()

    ds = sat["dataset"]
    bbox = sat["bbox"]

    ndvi = calculate_ndvi(ds)

    m = create_ndvi_overlay(ds)

    from streamlit_folium import st_folium

    st_folium(
    m,
    width=1200,
    height=700
)

# ==========================================
# FORECAST
# ==========================================

elif page == "Forecast":

    st.title("📈 24-Hour PM 2.5 Forecast")

    forecast = forecast_pm25(
        pm25,
        data["temperature"],
        data["wind"],
        data["rain"]
    )

    st.plotly_chart(
        forecast_chart(forecast),
        use_container_width=True
    )

    st.dataframe(
        forecast,
        use_container_width=True
    )

# ==========================================
# DISPERSION
# ==========================================

elif page == "Dispersion":

    st.title("🏭 Gaussian Plume Simulation")

    emission = st.slider(
        "PM 2.5 Emission (g/s)",
        10,
        500,
        120
    )

    wind = st.slider(
        "Wind Speed (m/s)",
        1,
        20,
        5
    )

    stack = st.slider(
        "Stack Height (m)",
        20,
        200,
        60
    )

    X, Y, C = gaussian_plume(
        emission,
        wind,
        stack
    )

    st.plotly_chart(
        plume_heatmap(X, Y, C),
        use_container_width=True
    )

    st.info(
        f"Emission = {emission} g/s | Wind = {wind} m/s | Stack Height = {stack} m"
    )

# ==========================================
# WATER QUALITY
# ==========================================

elif page == "Water Quality":

    st.title("💧 Water Quality Simulator")

    c1, c2 = st.columns(2)

    with c1:
        ph = st.slider("pH", 0.0, 14.0, 7.2)
        bod = st.slider("BOD (mg/L)", 0.0, 20.0, 2.5)

    with c2:
        cod = st.slider("COD (mg/L)", 0.0, 100.0, 18.0)
        do = st.slider("Dissolved Oxygen", 0.0, 14.0, 7.0)

    wqi, quality = calculate_wqi(
        ph,
        bod,
        cod,
        do
    )

    st.metric(
        "Water Quality Index",
        wqi
    )

    if quality == "Excellent":
        st.success("🟢 Excellent Water")

    elif quality == "Good":
        st.info("🔵 Good Water")

    elif quality == "Moderate":
        st.warning("🟡 Moderate Water")

    else:
        st.error("🔴 Polluted Water")

    st.divider()

    st.write("### Water Parameters")

    df = pd.DataFrame({
        "Parameter": [
            "pH",
            "BOD",
            "COD",
            "DO"
        ],
        "Value": [
            ph,
            bod,
            cod,
            do
        ]
    })

    st.dataframe(df, use_container_width=True)

# ==========================================
# CARBON SIMULATOR
# ==========================================

elif page == "Carbon Simulator":

    st.title("🌱 Carbon Emission Simulator")

    c1, c2 = st.columns(2)

    with c1:
        vehicles = st.slider(
            "🚗 Vehicles",
            0,
            10000,
            500
        )

        industries = st.slider(
            "🏭 Industries",
            0,
            100,
            10
        )

    with c2:
        trees = st.slider(
            "🌳 Existing Trees",
            0,
            50000,
            3000
        )

        solar = st.slider(
            "☀ Solar Energy (kWh/day)",
            0,
            5000,
            500
        )

    result = calculate_carbon(
        vehicles,
        industries,
        trees,
        solar
    )

    st.divider()

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "CO₂ Emitted",
        f"{result['total']} kg"
    )

    m2.metric(
        "CO₂ Absorbed",
        f"{result['absorbed']} kg"
    )

    m3.metric(
        "Net Carbon",
        f"{result['net']} kg"
    )

    m4.metric(
        "Score",
        f"{result['score']} %"
    )

    st.divider()

    st.plotly_chart(
        carbon_gauge(result["score"]),
        use_container_width=True
    )

    if result["score"] >= 80:
        st.success("🌿 Excellent Sustainable Region")

    elif result["score"] >= 60:
        st.info("Moderately Sustainable")

    else:
        st.error("High Carbon Emission Zone")

# ==========================================
# HISTORICAL DATA
# ==========================================

elif page == "Historical Data":

    st.title("💾 Historical Environmental Database")

    history = pd.read_csv(CSV)

    st.metric(
        "Total Records",
        len(history)
    )

    st.divider()

    st.dataframe(
        history,
        use_container_width=True
    )

    st.download_button(
        label="📥 Download CSV",
        data=history.to_csv(index=False),
        file_name="EcoSim_Historical_Data.csv",
        mime="text/csv"
    )

# ==========================================
# MICRO-CLIMATE ENGINE
# ==========================================

elif page == "Micro-Climate Engine":

    st.title("🌦 EcoSim Urban Micro-Climate Engine")

    st.write("Real-time Urban Heat Island Simulation")

    col1, col2, col3 = st.columns(3)

    with col1:
        vegetation = st.slider("🌿 Vegetation %", 0, 100, 35)

    with col2:
        builtup = st.slider("🏙 Built-up %", 0, 100, 55)

    with col3:
        water = st.slider("💧 Water %", 0, 100, 10)

    result = simulate_microclimate(
        temperature=data["temperature"],
        humidity=data["humidity"],
        wind_speed=data["wind"],
        vegetation_percent=vegetation,
        builtup_percent=builtup,
        water_percent=water,
        grid_size=20
    )

    st.divider()

    a, b, c, d = st.columns(4)

    a.metric("🌡 Surface Temp", f"{result['avg_temp']} °C")
    b.metric("🔥 Heat Island", result["heat_island"])
    c.metric("🌿 Cooling", result["cooling"])
    d.metric("🚨 Critical", result["critical_cells"])

    st.divider()

    st.plotly_chart(
        microclimate_heatmap(result["grid"]),
        use_container_width=True
    )

    st.subheader("Micro-Climate Grid Data")

    st.dataframe(
        result["grid"],
        use_container_width=True
    )

elif page == "AI Tree Species":

    st.title("🌳 AI Tree Species Recommendation")

    c1, c2 = st.columns(2)

    with c1:
        temp = st.slider(
            "Average Temperature (°C)",
            10,
            50,
            int(data["temperature"])
        )

        rainfall = st.slider(
            "Annual Rainfall (mm)",
            200,
            3000,
            800
        )

    with c2:
        soil = st.selectbox(
            "Soil Type",
            [
                "Alluvial",
                "Black",
                "Clay",
                "Sandy"
            ]
        )

    species = recommend_species(
        temp,
        rainfall,
        soil
    )

    st.subheader("Best Native Species")

    st.dataframe(
        species,
        use_container_width=True
    )

    best = species.iloc[0]

    st.success(
        f"Recommended Tree: {best['Species']} ({best['Suitability %']}% suitability)"
    )