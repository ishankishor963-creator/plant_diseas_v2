import pandas as pd
import streamlit as st

from utils.esp_client import get_sensor_data
from utils.theme import inject_theme, stat_card

inject_theme()

st.title("🌡️ Sensor Dashboard")

if "sensor_history" not in st.session_state:
    st.session_state["sensor_history"] = []

col_a, col_b = st.columns([1, 3])
with col_a:
    refresh = st.button("🔄 Refresh reading", use_container_width=True)
with col_b:
    auto = st.checkbox("Auto-refresh every 10s")

if refresh or not st.session_state["sensor_history"]:
    reading = get_sensor_data()
    st.session_state["sensor_history"].append(reading)
    st.session_state["sensor_history"] = st.session_state["sensor_history"][-100:]

latest = st.session_state["sensor_history"][-1]

if latest["source"] == "demo":
    st.warning(
        "Showing demo data — set your device URL in the sidebar to see "
        "live sensor readings.",
        icon="⚠️",
    )

c1, c2, c3 = st.columns(3)
with c1:
    stat_card("soil_moisture", "💧", "Soil moisture", latest["soil_moisture"], "%")
with c2:
    stat_card("humidity", "🌫️", "Humidity", latest["humidity"], "%")
with c3:
    stat_card("temperature", "🌡️", "Temperature", latest["temperature"], "°C")
st.caption(f"Last updated: {latest['timestamp']} ({latest['source']} data)")

st.divider()
st.subheader("Trend")
if len(st.session_state["sensor_history"]) > 1:
    df = pd.DataFrame(st.session_state["sensor_history"])
    df = df.set_index("timestamp")[["soil_moisture", "humidity", "temperature"]]
    st.line_chart(df)
else:
    st.info("Refresh a few times to build up a trend chart.")

if auto:
    import time
    time.sleep(10)
    st.rerun()
