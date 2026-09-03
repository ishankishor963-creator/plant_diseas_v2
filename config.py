"""
Central configuration for Agro Edge.

Every sensor below is looked up through SENSOR_CHANNELS, so once a board is
online you only need to fill in its channel_id / read_api_key / field here.
Until a channel_id is set, the matching page will clearly say "sensor not
configured yet" instead of crashing, and (where sensible) will fall back to
ambient weather data.

Typical layout for a 4-board setup:
  Board 1 (already live): soil moisture          -> existing channel 3467712
  Board 2: temperature + humidity (DHT/SHT)       -> one channel, 2 fields
  Board 3: water level / rain gauge (flood)       -> own channel
  Board 4: ESP32-S3 + OV2640 camera + LoRa uplink -> not on ThingSpeak;
           see pages/1_Live_Camera.py for how the live/webcam feed plugs in.
"""

import streamlit as st

SENSOR_CHANNELS = {
    "soil_moisture": {
        "channel_id": "3467712",       # your existing board — already live
        "read_api_key": "GV82FOVOEX7A2MQU",
        "field": 1,
        "unit": "%",
    },
    "temperature": {
        "channel_id": None,            # fill in once the temp/humidity ESP32 is online
        "read_api_key": None,
        "field": 1,
        "unit": "°C",
    },
    "humidity": {
        "channel_id": None,            # can be the SAME channel_id as temperature,
        "read_api_key": None,          # just a different field number
        "field": 2,
        "unit": "%",
    },
    "water_level": {
        "channel_id": None,            # flood/water-level sensor board
        "read_api_key": None,
        "field": 1,
        "unit": "%",
    },
}

# Secrets (set these in .streamlit/secrets.toml when you deploy)
OPENWEATHER_API_KEY = st.secrets.get("OPENWEATHER_API_KEY", None)
ANTHROPIC_API_KEY = st.secrets.get("ANTHROPIC_API_KEY", None)

# Model used for the "Ask the Plant AI" agent. Check your Anthropic Console /
# docs.claude.com for the exact current model string available on your account
# and swap this if needed.
CLAUDE_MODEL = "claude-sonnet-5"

# Flood / drought alert thresholds — these are a starting point. Tune them
# once your sensors are calibrated against real field conditions.
THRESHOLDS = {
    "drought_soil_max": 25,       # soil moisture % at/below this = drought signal
    "drought_humidity_max": 35,   # ambient/board humidity % at/below this = drought signal
    "flood_soil_min": 85,         # soil moisture % at/above this = flood signal
    "flood_water_level_min": 70,  # water-level sensor % at/above this = flood signal
    "flood_humidity_min": 85,     # humidity % at/above this = flood signal
}

# How many corroborating signals are required before we call it an actual
# alert (vs. just showing normal readings). Defaults to 2-of-N so a single
# noisy sensor reading doesn't trigger a false alarm.
MIN_SIGNALS_FOR_ALERT = 2
