import streamlit as st

from utils.theme import inject_theme, feature_card_header

st.set_page_config(
    page_title="Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
)

# --- One-time session state defaults ---
if "esp_base_url" not in st.session_state:
    st.session_state["esp_base_url"] = ""


def home():
    inject_theme()

    # --- Sidebar: device connection setup (shared across all pages) ---
    with st.sidebar:
        st.header("🔌 Device Connection")
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
        if st.session_state["esp_base_url"]:
            st.success("Device URL set — pages will try to fetch live data.")
        else:
            st.info("No device URL set — pages will show demo data.")

    st.title("🌾 Smart Farming Assistant")
    st.markdown(
        "An edge-AI powered dashboard for early crop disease detection, "
        "environmental monitoring, and climate-resilience alerts."
    )

    st.divider()

    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)

    with col1:
        feature_card_header(
            "ai_assistant", "🤖", "AI Assistant",
            "Ask farming questions and get instant answers.",
        )
        st.page_link(ai_page, label="Open AI Assistant", icon="🤖")

    with col2:
        feature_card_header(
            "sensor_dashboard", "🌡️", "Sensor Dashboard",
            "Live soil moisture, humidity, and temperature readings.",
        )
        st.page_link(sensor_page, label="Open Sensor Dashboard", icon="🌡️")

    with col3:
        feature_card_header(
            "alerts", "🚨", "Flood / Drought Alerts",
            "Early warnings based on sensor trends and rainfall forecast.",
        )
        st.page_link(alerts_page, label="Open Alerts", icon="🚨")

    with col4:
        feature_card_header(
            "camera_feed", "📷", "Camera Feed",
            "Live snapshot from your connected field camera.",
        )
        st.page_link(camera_page, label="Open Camera Feed", icon="📷")

    st.divider()
    feature_card_header(
        "disease_detection", "🔬", "AI Disease Detection",
        "Upload a leaf photo or use your camera to detect crop disease.",
    )
    st.page_link(disease_page, label="Open Disease Detection", icon="🔬")


# --- Explicit page registration (replaces implicit pages/ folder discovery) ---
home_page = st.Page(home, title="Home", icon="🌾", default=True)
ai_page = st.Page("pages/1_AI_Assistant.py", title="AI Assistant", icon="🤖")
sensor_page = st.Page("pages/2_Sensor_Dashboard.py", title="Sensor Dashboard", icon="🌡️")
alerts_page = st.Page("pages/3_Flood_Drought_Alerts.py", title="Flood/Drought Alerts", icon="🚨")
camera_page = st.Page("pages/4_Camera_Feed.py", title="Camera Feed", icon="📷")
disease_page = st.Page("pages/5_Disease_Detection.py", title="Disease Detection", icon="🔬")

pg = st.navigation([home_page, ai_page, sensor_page, alerts_page, camera_page, disease_page])
pg.run()
