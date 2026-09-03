"""Generic ThingSpeak read helpers. Every sensor (soil, temp, humidity,
water-level) is fetched through the same two functions — only the
channel_id / read_api_key / field differ, and those live in config.py.
"""

import requests
import streamlit as st


@st.cache_data(ttl=60, show_spinner=False)
def fetch_latest(channel_id, read_api_key, field):
    """Return {'value': float, 'timestamp': str} for the latest reading,
    or None if the channel isn't configured yet or the request fails."""
    if not channel_id:
        return None
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
    params = {"results": 1}
    if read_api_key:
        params["api_key"] = read_api_key
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            feeds = r.json().get("feeds")
            if feeds:
                feed = feeds[0]
                val = feed.get(f"field{field}")
                return {
                    "value": float(val) if val is not None else None,
                    "timestamp": feed.get("created_at"),
                }
        return None
    except requests.exceptions.RequestException:
        return None


@st.cache_data(ttl=60, show_spinner=False)
def fetch_history(channel_id, read_api_key, field, results=50):
    """Return a list of {'time': str, 'value': float} for charting, or None."""
    if not channel_id:
        return None
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json"
    params = {"results": results}
    if read_api_key:
        params["api_key"] = read_api_key
    try:
        r = requests.get(url, params=params, timeout=10)
        if r.status_code == 200:
            feeds = r.json().get("feeds", [])
            out = []
            for f in feeds:
                val = f.get(f"field{field}")
                if val is not None:
                    out.append({"time": f.get("created_at"), "value": float(val)})
            return out
        return None
    except requests.exceptions.RequestException:
        return None


def fetch_sensor_latest(sensor_key, channels_config):
    """Convenience wrapper: look up a sensor by name in config.SENSOR_CHANNELS."""
    cfg = channels_config[sensor_key]
    return fetch_latest(cfg["channel_id"], cfg["read_api_key"], cfg["field"])


def fetch_sensor_history(sensor_key, channels_config, results=50):
    cfg = channels_config[sensor_key]
    return fetch_history(cfg["channel_id"], cfg["read_api_key"], cfg["field"], results)
