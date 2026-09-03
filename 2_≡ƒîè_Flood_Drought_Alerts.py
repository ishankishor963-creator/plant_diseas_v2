import streamlit as st

from config import SENSOR_CHANNELS, OPENWEATHER_API_KEY
from sensors import fetch_sensor_latest
from theme import apply_theme, render_header, render_footer
from weather_utils import get_weather, get_weather_theme, render_weather_theme, compute_alert

st.set_page_config(page_title="Flood & Drought Alerts — Agro Edge", page_icon="🌊", layout="centered")
apply_theme()
render_header("Flood & Drought Alerts", "warning", "Field risk monitor")

city = st.text_input("Location", placeholder="📍 Enter your field's city/location for the rainfall signal",
                      label_visibility="collapsed")

weather_data = None
if city and OPENWEATHER_API_KEY:
    weather_data = get_weather(city, OPENWEATHER_API_KEY)
    if weather_data:
        theme = get_weather_theme(weather_data["weather"][0]["main"], weather_data["main"]["temp"])
        render_weather_theme(theme)
elif city and not OPENWEATHER_API_KEY:
    st.markdown('<div class="glass-card"><p class="hero-desc-text">Add OPENWEATHER_API_KEY to app secrets to include the rainfall signal in this alert.</p></div>', unsafe_allow_html=True)

soil = fetch_sensor_latest("soil_moisture", SENSOR_CHANNELS)
humidity_sensor = fetch_sensor_latest("humidity", SENSOR_CHANNELS)
water_level = fetch_sensor_latest("water_level", SENSOR_CHANNELS)

soil_pct = soil["value"] if soil else None
# Prefer your own humidity sensor once it's online; fall back to ambient
# weather humidity so the alert still works with just one board deployed.
humidity_pct = humidity_sensor["value"] if humidity_sensor else (
    weather_data["main"]["humidity"] if weather_data else None
)
water_level_pct = water_level["value"] if water_level else None
condition = weather_data["weather"][0]["main"] if weather_data else None

level, signals = compute_alert(soil_pct, humidity_pct, water_level_pct, condition)

signal_html = "".join(f'<p class="alert-signal">• {s}</p>' for s in signals)

if level == "flood":
    banner = f"""
    <div class="alert-banner flood">
        <div class="label-mono"><span class="material-symbols-outlined">flood</span>Flood Risk</div>
        <div class="alert-title">⚠ Elevated flood risk detected</div>
        {signal_html}
    </div>"""
elif level == "drought":
    banner = f"""
    <div class="alert-banner drought">
        <div class="label-mono"><span class="material-symbols-outlined">local_fire_department</span>Drought Risk</div>
        <div class="alert-title">⚠ Elevated drought risk detected</div>
        {signal_html}
    </div>"""
else:
    banner = f"""
    <div class="alert-banner normal">
        <div class="label-mono"><span class="material-symbols-outlined">check_circle</span>Status</div>
        <div class="alert-title">Conditions normal</div>
        {signal_html}
    </div>"""
st.markdown(banner, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Underlying readings, so you can see exactly what fed the call above
# ---------------------------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    val = f"{soil_pct:.0f}%" if soil_pct is not None else "—"
    st.markdown(f"""
    <div class="glass-card metric-tile">
        <div class="label-mono"><span class="material-symbols-outlined">water_drop</span>Soil Moisture</div>
        <div class="metric-value">{val}</div>
        {'<p class="hero-desc-text">Board not configured yet — set it in config.py</p>' if soil_pct is None else ''}
    </div>
    """, unsafe_allow_html=True)
with c2:
    val = f"{humidity_pct:.0f}%" if humidity_pct is not None else "—"
    source = "board" if humidity_sensor else ("ambient weather" if weather_data else "not available")
    st.markdown(f"""
    <div class="glass-card metric-tile">
        <div class="label-mono"><span class="material-symbols-outlined">humidity_percentage</span>Humidity</div>
        <div class="metric-value">{val}</div>
        <p class="hero-desc-text">Source: {source}</p>
    </div>
    """, unsafe_allow_html=True)
with c3:
    val = f"{water_level_pct:.0f}%" if water_level_pct is not None else "—"
    st.markdown(f"""
    <div class="glass-card metric-tile">
        <div class="label-mono"><span class="material-symbols-outlined">waves</span>Water Level</div>
        <div class="metric-value">{val}</div>
        {'<p class="hero-desc-text">Board not deployed yet — set it in config.py</p>' if water_level_pct is None else ''}
    </div>
    """, unsafe_allow_html=True)

render_footer()
