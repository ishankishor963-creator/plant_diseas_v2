import pandas as pd
import streamlit as st

from utils.esp_client import get_sensor_data
from utils.theme import inject_theme, topnav
from utils.auth import logout_button

inject_theme()
with st.sidebar:
    logout_button()
topnav("sensor")

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
c1.metric("Soil Moisture", f"{latest['soil_moisture']}%")
c2.metric("Humidity", f"{latest['humidity']}%")
c3.metric("Temperature", f"{latest['temperature']}°C")
st.caption(f"Last updated: {latest['timestamp']} ({latest['source']} data)")

st.divider()
st.subheader("Signal Timeline")
if len(st.session_state["sensor_history"]) > 1:
    import plotly.graph_objects as go

    df = pd.DataFrame(st.session_state["sensor_history"])
    fig = go.Figure()
    colors = {"soil_moisture": "#22d3ee", "humidity": "#8b5cf6", "temperature": "#f5b942"}
    for col, color in colors.items():
        fig.add_trace(go.Scatter(
            x=df["timestamp"], y=df[col], mode="lines+markers", name=col.replace("_", " ").title(),
            line=dict(color=color, width=2), marker=dict(size=6, line=dict(width=1, color="#0a0812")),
        ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#b8b7c9", family="Inter"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, color="#7d7c94"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", color="#7d7c94"),
        height=360,
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Refresh a few times to build up a trend chart.")

if auto:
    import time
    time.sleep(10)
    st.rerun()
