import time

import streamlit as st

from utils.esp_client import get_camera_snapshot, get_device_base_url
from utils.theme import inject_theme, topnav
from utils.auth import logout_button

inject_theme()
with st.sidebar:
    logout_button()
topnav("camera")

st.title("📷 Field Camera Feed")

col_a, col_b = st.columns([1, 3])
with col_a:
    refresh = st.button("🔄 Refresh snapshot", use_container_width=True)
with col_b:
    auto = st.checkbox("Auto-refresh every 5s")

if not get_device_base_url():
    st.info(
        "No device URL set in the sidebar — connect your ESP32-CAM (or "
        "similar) and set its address to see the live feed here.",
        icon="ℹ️",
    )

image_bytes = get_camera_snapshot()

if image_bytes:
    st.image(image_bytes, caption=f"Last refreshed: {time.strftime('%H:%M:%S')}", use_container_width=True)
else:
    st.warning(
        "Couldn't fetch a snapshot from the device. Showing a placeholder — "
        "check the device is powered on and reachable at the URL in the sidebar.",
        icon="⚠️",
    )
    st.image(
        "https://placehold.co/800x450?text=No+Camera+Feed",
        use_container_width=True,
    )

if auto:
    time.sleep(5)
    st.rerun()
