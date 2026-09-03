import streamlit as st

from config import SENSOR_CHANNELS, OPENWEATHER_API_KEY
from sensors import fetch_sensor_latest, fetch_sensor_history
from theme import apply_theme, render_header, render_footer, gauge_color
from weather_utils import get_weather

st.set_page_config(page_title="Temperature & Humidity — Agro Edge", page_icon="🌡️", layout="centered")
apply_theme()
render_header("Temperature & Humidity", "thermostat", "Field microclimate")

temp = fetch_sensor_latest("temperature", SENSOR_CHANNELS)
humidity = fetch_sensor_latest("humidity", SENSOR_CHANNELS)

# Fall back to ambient weather for whichever reading doesn't have a board yet
city = None
weather_data = None
if temp is None or humidity is None:
    city = st.text_input("Location", placeholder="📍 Enter a location for the ambient fallback reading",
                          label_visibility="collapsed")
    if city and OPENWEATHER_API_KEY:
        weather_data = get_weather(city, OPENWEATHER_API_KEY)

temp_val = temp["value"] if temp else (weather_data["main"]["temp"] if weather_data else None)
temp_source = "board" if temp else ("ambient weather" if weather_data else None)
humidity_val = humidity["value"] if humidity else (weather_data["main"]["humidity"] if weather_data else None)
humidity_source = "board" if humidity else ("ambient weather" if weather_data else None)

c1, c2 = st.columns(2)
with c1:
    if temp_val is not None:
        st.markdown(f"""
        <div class="glass-card metric-tile">
            <div class="label-mono"><span class="material-symbols-outlined">thermostat</span>Temperature</div>
            <div class="metric-value">{temp_val:.1f}°C</div>
            <p class="hero-desc-text">Source: {temp_source}{' · ' + temp['timestamp'] if temp else ''}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card metric-tile">
            <div class="label-mono"><span class="material-symbols-outlined">thermostat</span>Temperature</div>
            <p class="hero-desc-text">Board not configured yet — set channel in config.py, or enter a location above for an ambient reading.</p>
        </div>
        """, unsafe_allow_html=True)

with c2:
    if humidity_val is not None:
        color = gauge_color(humidity_val)
        st.markdown(f"""
        <div class="glass-card metric-tile">
            <div class="label-mono"><span class="material-symbols-outlined">humidity_percentage</span>Humidity</div>
            <div class="metric-value">{humidity_val:.0f}%</div>
            <div class="progress-track"><div class="progress-fill" style="width:{humidity_val:.0f}%; background:{color};"></div></div>
            <p class="hero-desc-text" style="margin-top:0.5rem;">Source: {humidity_source}{' · ' + humidity['timestamp'] if humidity else ''}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card metric-tile">
            <div class="label-mono"><span class="material-symbols-outlined">humidity_percentage</span>Humidity</div>
            <p class="hero-desc-text">Board not configured yet — set channel in config.py, or enter a location above for an ambient reading.</p>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Historical trend — only available once the ESP32 board is actually
# reporting to ThingSpeak (ambient weather has no history here)
# ---------------------------------------------------------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown('<div class="label-mono"><span class="material-symbols-outlined">show_chart</span>Recent Trend (last 50 readings)</div>', unsafe_allow_html=True)

temp_history = fetch_sensor_history("temperature", SENSOR_CHANNELS)
humidity_history = fetch_sensor_history("humidity", SENSOR_CHANNELS)

if temp_history:
    st.caption("Temperature (°C)")
    st.line_chart({"Temperature": [p["value"] for p in temp_history]})
if humidity_history:
    st.caption("Humidity (%)")
    st.line_chart({"Humidity": [p["value"] for p in humidity_history]})
if not temp_history and not humidity_history:
    st.markdown('<p class="hero-desc-text">No historical data yet — this fills in automatically once the temp/humidity ESP32 board is reporting to its ThingSpeak channel (set in config.py).</p>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
render_footer()
