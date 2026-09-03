import requests
import streamlit as st

from utils.esp_client import get_sensor_data

st.set_page_config(page_title="Flood / Drought Alerts", page_icon="🚨", layout="wide")
st.title("🚨 Flood / Drought Alerts")
st.caption(
    "Combines your live soil moisture reading with a rainfall forecast "
    "to flag flood or drought risk early."
)

with st.sidebar:
    st.header("⚙️ Alert Thresholds")
    drought_threshold = st.slider("Drought warning below (%)", 0, 50, 25)
    flood_moisture_threshold = st.slider("Flood warning above (%)", 50, 100, 80)
    heavy_rain_mm = st.slider("Heavy-rain warning (mm/24h)", 10, 150, 50)
    st.divider()
    st.caption("Field location (for rainfall forecast)")
    lat = st.number_input("Latitude", value=12.9716, format="%.4f")
    lon = st.number_input("Longitude", value=77.5946, format="%.4f")


@st.cache_data(ttl=1800)
def get_rainfall_forecast(lat: float, lon: float):
    """Free rainfall forecast via Open-Meteo — no API key required."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=precipitation_sum&forecast_days=3&timezone=auto"
    )
    resp = requests.get(url, timeout=8)
    resp.raise_for_status()
    data = resp.json()
    return list(zip(data["daily"]["time"], data["daily"]["precipitation_sum"]))


reading = get_sensor_data()
if reading["source"] == "demo":
    st.warning(
        "Soil moisture is demo data — set your device URL in the "
        "sidebar for real readings.",
        icon="⚠️",
    )

moisture = reading["soil_moisture"]

try:
    forecast = get_rainfall_forecast(lat, lon)
    forecast_ok = True
except Exception:
    forecast = []
    forecast_ok = False
    st.info("Couldn't reach the rainfall forecast service — showing soil-only alerts.")

today_rain = forecast[0][1] if forecast else 0

st.subheader("Current Status")
c1, c2 = st.columns(2)
c1.metric("Soil Moisture", f"{moisture}%")
c2.metric("Rain forecast (today)", f"{today_rain} mm" if forecast_ok else "N/A")

st.divider()

if moisture is not None and moisture >= flood_moisture_threshold:
    st.error(
        f"🌊 **Flood risk** — soil moisture ({moisture}%) is at or above "
        f"your {flood_moisture_threshold}% threshold. Ensure drainage "
        "channels are clear.",
        icon="🚨",
    )
elif forecast_ok and today_rain >= heavy_rain_mm:
    st.error(
        f"🌊 **Flood risk** — {today_rain}mm of rain forecast today "
        f"exceeds your {heavy_rain_mm}mm threshold, on top of "
        f"{moisture}% soil moisture.",
        icon="🚨",
    )
elif moisture is not None and moisture <= drought_threshold:
    st.warning(
        f"🌵 **Drought risk** — soil moisture ({moisture}%) is at or "
        f"below your {drought_threshold}% threshold. Consider "
        "irrigating soon.",
        icon="⚠️",
    )
else:
    st.success("✅ No flood or drought risk detected right now.", icon="✅")

if forecast_ok:
    st.divider()
    st.subheader("3-Day Rainfall Forecast")
    for day, mm in forecast:
        st.write(f"**{day}**: {mm} mm")
