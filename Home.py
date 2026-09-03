import streamlit as st

st.set_page_config(
    page_title="Smart Farming Assistant",
    page_icon="🌾",
    layout="wide",
)

# --- One-time session state defaults ---
if "esp_base_url" not in st.session_state:
    st.session_state["esp_base_url"] = ""

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
    st.subheader("🤖 AI Assistant")
    st.write("Ask farming questions and get instant answers.")
    st.page_link("pages/1_AI_Assistant.py", label="Open AI Assistant", icon="🤖")

with col2:
    st.subheader("🌡️ Sensor Dashboard")
    st.write("Live soil moisture, humidity, and temperature readings.")
    st.page_link("pages/2_Sensor_Dashboard.py", label="Open Sensor Dashboard", icon="🌡️")

with col3:
    st.subheader("🚨 Flood / Drought Alerts")
    st.write("Early warnings based on sensor trends and rainfall forecast.")
    st.page_link("pages/3_Flood_Drought_Alerts.py", label="Open Alerts", icon="🚨")

with col4:
    st.subheader("📷 Camera Feed")
    st.write("Live snapshot from your connected field camera.")
    st.page_link("pages/4_Camera_Feed.py", label="Open Camera Feed", icon="📷")

st.divider()
st.subheader("🔬 AI Disease Detection")
st.write("Upload a leaf photo or use your camera to detect crop disease.")
st.page_link("pages/5_Disease_Detection.py", label="Open Disease Detection", icon="🔬")
