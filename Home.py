import streamlit as st

from utils.auth import require_login, logout_button
from utils.theme import inject_theme, topnav
from utils.esp_client import get_sensor_data

# --- Auth gate: nothing below this line renders until logged in ---
require_login()

st.set_page_config(
    page_title="AgroSentry — Farm Ops",
    page_icon="🌾",
    layout="wide",
)

# --- One-time session state defaults ---
if "esp_base_url" not in st.session_state:
    st.session_state["esp_base_url"] = ""

inject_theme()


def feature_card(col, icon, title, desc, target, chip_label, chip_class):
    with col:
        with st.container(border=True):
            st.markdown('<div class="card-marker"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<span class="chip {chip_class}">{chip_label}</span>',
                unsafe_allow_html=True,
            )
            st.markdown(f"### {icon} {title}")
            st.write(desc)
            if st.button(f"Open {title}", key=f"open_{title}", use_container_width=True):
                st.switch_page(target)


def home():
    # --- Sidebar: device connection, styled as a detail panel ---
    with st.sidebar:
        st.markdown("### 🔌 Device Status")
        connected = bool(st.session_state["esp_base_url"])
        chip = '<span class="chip chip-green">Connected</span>' if connected else '<span class="chip chip-amber">Demo Mode</span>'
        st.markdown(chip, unsafe_allow_html=True)
        st.write("")
        st.session_state["esp_base_url"] = st.text_input(
            "ESP32 / Raspberry Pi base URL",
            value=st.session_state["esp_base_url"],
            placeholder="http://192.168.1.42",
            help=(
                "The IP address your ESP32/Pi prints over serial when it "
                "connects to WiFi. Leave blank to run every page in demo "
                "mode with sample data."
            ),
        )
        if connected:
            st.success("Pages will try to fetch live data.")
        else:
            st.info("Pages will show demo data.")
        st.divider()
        logout_button()

    topnav("home")

    st.title("🌾 Farm Ops Dashboard")
    st.markdown(
        "Edge-AI monitoring for early crop disease detection, "
        "environmental sensing, and climate-resilience alerts — all in one place."
    )

    # --- Quick-glance strip, pulling one live/demo reading ---
    reading = get_sensor_data()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Soil Moisture", f"{reading['soil_moisture']}%")
    c2.metric("Humidity", f"{reading['humidity']}%")
    c3.metric("Temperature", f"{reading['temperature']}°C")
    c4.metric("Data Source", "Live" if reading["source"] == "device" else "Demo")

    st.write("")
    st.divider()
    st.subheader("Modules")

    row1 = st.columns(3)
    row2 = st.columns(3)

    feature_card(row1[0], "🤖", "AI Assistant", "Ask farming questions and get instant answers.", "pages/1_AI_Assistant.py", "Assistant", "chip-cyan")
    feature_card(row1[1], "🌡️", "Sensor Dashboard", "Live soil moisture, humidity, and temperature readings.", "pages/2_Sensor_Dashboard.py", "Live", "chip-green")
    feature_card(row1[2], "🚨", "Flood / Drought Alerts", "Early warnings from sensor trends and rainfall forecast.", "pages/3_Flood_Drought_Alerts.py", "Alerts", "chip-pink")
    feature_card(row2[0], "📷", "Camera Feed", "Live snapshot from your connected field camera.", "pages/4_Camera_Feed.py", "Camera", "chip-cyan")
    feature_card(row2[1], "🔬", "Disease Detection", "Upload a leaf photo to detect crop disease with AI.", "pages/5_Disease_Detection.py", "AI Model", "chip-amber")


# --- Explicit page registration (replaces implicit pages/ folder discovery) ---
home_page = st.Page(home, title="Home", icon="🌾", default=True)
ai_page = st.Page("pages/1_AI_Assistant.py", title="AI Assistant", icon="🤖")
sensor_page = st.Page("pages/2_Sensor_Dashboard.py", title="Sensor Dashboard", icon="🌡️")
alerts_page = st.Page("pages/3_Flood_Drought_Alerts.py", title="Flood/Drought Alerts", icon="🚨")
camera_page = st.Page("pages/4_Camera_Feed.py", title="Camera Feed", icon="📷")
disease_page = st.Page("pages/5_Disease_Detection.py", title="Disease Detection", icon="🔬")


# Registry so the custom top nav (in utils/theme.py) can switch_page() to
# Home specifically, since it's a callable-based page rather than a file.
st.session_state["_pages"] = {
    "home": home_page,
    "ai": "pages/1_AI_Assistant.py",
    "sensor": "pages/2_Sensor_Dashboard.py",
    "alerts": "pages/3_Flood_Drought_Alerts.py",
    "camera": "pages/4_Camera_Feed.py",
    "disease": "pages/5_Disease_Detection.py",
}

pg = st.navigation(
    [home_page, ai_page, sensor_page, alerts_page, camera_page, disease_page],
    position="hidden",
)
pg.run()
