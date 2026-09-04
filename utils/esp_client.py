"""
esp_client.py
--------------
Talks to the ESP32 / Raspberry Pi that hosts a small HTTP API for your
sensors and camera. If the device isn't reachable (e.g. you're still
developing, or the hardware is off), every function falls back to
realistic demo data so the rest of the app keeps working.

EXPECTED DEVICE API (adjust to match your firmware):
    GET  http://<device-ip>/data
         -> {"soil_moisture": 42.5, "humidity": 61.2, "temperature": 27.8}

    GET  http://<device-ip>/capture
         -> raw JPEG bytes (image/jpeg)

If your firmware uses different routes or JSON keys, just edit the
paths/keys below — the rest of the app doesn't need to change.
"""

import random
import time
from io import BytesIO

import requests
import streamlit as st

DATA_ENDPOINT = "/data"
CAMERA_ENDPOINT = "/capture"
TIMEOUT_SECONDS = 4


def get_device_base_url() -> str:
    """Reads the device's base URL from session state (set in the sidebar)."""
    return st.session_state.get("esp_base_url", "").strip().rstrip("/")


def _demo_sensor_reading() -> dict:
    """Fake-but-plausible sensor values, used when the device is unreachable."""
    return {
        "soil_moisture": round(random.uniform(15, 70), 1),  # %
        "humidity": round(random.uniform(30, 90), 1),       # %
        "temperature": round(random.uniform(18, 38), 1),    # deg C
        "timestamp": time.strftime("%H:%M:%S"),
        "source": "demo",
    }


def get_sensor_data() -> dict:
    """
    Fetches the latest soil moisture / humidity / temperature reading.
    Returns a dict with a "source" key of "device" or "demo" so pages
    can show a banner when they're looking at fake data.
    """
    base_url = get_device_base_url()
    if not base_url:
        return _demo_sensor_reading()

    try:
        resp = requests.get(f"{base_url}{DATA_ENDPOINT}", timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        payload = resp.json()
        return {
            "soil_moisture": payload.get("soil_moisture"),
            "humidity": payload.get("humidity"),
            "temperature": payload.get("temperature"),
            "timestamp": time.strftime("%H:%M:%S"),
            "source": "device",
        }
    except Exception as e:
        st.session_state["esp_last_error"] = str(e)
        return _demo_sensor_reading()


def get_camera_snapshot():
    """
    Fetches a single JPEG frame from the ESP32-CAM (or similar).
    Returns raw bytes on success, or None if the device is unreachable
    (the calling page should handle showing a placeholder in that case).
    """
    base_url = get_device_base_url()
    if not base_url:
        return None

    try:
        resp = requests.get(f"{base_url}{CAMERA_ENDPOINT}", timeout=TIMEOUT_SECONDS)
        resp.raise_for_status()
        return BytesIO(resp.content)
    except Exception as e:
        st.session_state["esp_last_error"] = str(e)
        return None
