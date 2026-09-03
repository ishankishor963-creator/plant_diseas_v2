"""Ambient weather (OpenWeatherMap), the animated weather-reactive background
effects, and the combined flood/drought scoring logic (soil + humidity +
rainfall condition)."""

import random

import requests
import streamlit as st

from config import THRESHOLDS, MIN_SIGNALS_FOR_ALERT

WEATHER_ICON_MAP = {
    "rain": "rainy", "drizzle": "rainy", "thunderstorm": "thunderstorm",
    "snow": "ac_unit", "clear": "sunny", "clouds": "cloud",
    "mist": "foggy", "fog": "foggy", "haze": "foggy", "smoke": "foggy",
}


def get_weather(city_name, api_key):
    if not api_key:
        return None
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city_name, "appid": api_key, "units": "metric"}
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None


def get_weather_theme(condition_main, temp=None):
    c = (condition_main or "").lower()
    if c in ("rain", "drizzle"):
        return {"accent": "#8ED1E8", "accent2": "#E0F2F1", "glow": "rgba(224,242,241,0.22)", "effect": "rain", "mode_class": "rain-mode"}
    if c == "thunderstorm":
        return {"accent": "#B39DDB", "accent2": "#9575CD", "glow": "rgba(126,87,194,0.3)", "effect": "thunder", "mode_class": "rain-mode"}
    if c == "snow" or (temp is not None and temp <= 2):
        return {"accent": "#E0F2F1", "accent2": "#B8E6E0", "glow": "rgba(224,247,250,0.25)", "effect": "snow", "mode_class": "snow-mode"}
    if c == "clear":
        return {"accent": "#F2C94C", "accent2": "#e9c349", "glow": "rgba(242,201,76,0.3)", "effect": "sun", "mode_class": "sun-mode"}
    if c == "clouds":
        return {"accent": "#B0BEC5", "accent2": "#90A4AE", "glow": "rgba(176,190,197,0.2)", "effect": "clouds", "mode_class": "cloud-mode"}
    if c in ("mist", "fog", "haze", "smoke"):
        return {"accent": "#CFD8DC", "accent2": "#B0BEC5", "glow": "rgba(207,216,220,0.18)", "effect": "fog", "mode_class": "cloud-mode"}
    return None


def render_weather_theme(theme):
    if not theme:
        return
    st.markdown(f"""
    <style>
    :root {{ --accent: {theme['accent']}; --accent-2: {theme['accent2']}; --glow: {theme['glow']}; }}
    </style>
    <script>
        const body = window.parent.document.querySelector('body');
        if (body) {{
            body.classList.remove('rain-mode', 'snow-mode', 'sun-mode', 'cloud-mode');
            body.classList.add('{theme['mode_class']}');
        }}
    </script>
    """, unsafe_allow_html=True)

    effect = theme["effect"]
    if effect in ("rain", "thunder"):
        drops = "".join(
            f'<div class="raindrop" style="left:{random.uniform(0,100):.1f}%; height:{random.uniform(50,95):.0f}px; '
            f'animation-delay:{random.uniform(0,2):.2f}s; animation-duration:{random.uniform(0.5,1.2):.2f}s;"></div>'
            for _ in range(38)
        )
        flash_html = '<div class="lightning-flash"></div>' if effect == "thunder" else ""
        st.markdown(f'<div class="weather-overlay">{drops}</div>{flash_html}', unsafe_allow_html=True)
    elif effect == "snow":
        flakes = "".join(
            f'<div class="snowflake" style="left:{random.uniform(0,100):.1f}%; width:{random.uniform(3,8):.1f}px; height:{random.uniform(3,8):.1f}px; '
            f'animation-delay:{random.uniform(0,5):.2f}s; animation-duration:{random.uniform(4,9):.2f}s;"></div>'
            for _ in range(30)
        )
        st.markdown(f'<div class="weather-overlay">{flakes}</div>', unsafe_allow_html=True)
    elif effect == "sun":
        st.markdown('<div class="weather-overlay"><div class="sun-glow"></div><div class="sun-rays"></div></div>', unsafe_allow_html=True)
    elif effect in ("clouds", "fog"):
        st.markdown(f"""
        <div class="weather-overlay">
            <div class="cloud-blob" style="top:8%; width:220px; height:80px; background:{theme['glow']}; animation-duration:38s;"></div>
            <div class="cloud-blob" style="top:28%; width:160px; height:60px; background:{theme['glow']}; animation-duration:28s; animation-delay:-10s;"></div>
            <div class="cloud-blob" style="top:52%; width:260px; height:90px; background:{theme['glow']}; animation-duration:45s; animation-delay:-20s;"></div>
        </div>
        """, unsafe_allow_html=True)


def get_irrigation_tip(weather_data):
    condition = weather_data["weather"][0]["main"].lower()
    temp = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]
    if "rain" in condition or "drizzle" in condition or "thunderstorm" in condition:
        return "🌧️ Rain detected — delay watering to avoid overwatering and root issues."
    elif temp > 32 and humidity < 40:
        return "☀️ Hot and dry conditions — consider watering soon, ideally early morning or evening to reduce evaporation."
    elif humidity > 80:
        return "💧 High humidity — go easy on watering, and monitor for fungal disease risk."
    else:
        return "🌤️ Conditions look moderate — water as per your crop's normal schedule."


def compute_alert(soil_pct, humidity_pct, water_level_pct, weather_condition):
    """Combine soil moisture + humidity + rainfall condition (+ optional
    water-level sensor once you have one) into a flood/drought call.

    Returns (level, signals) where level is "flood" | "drought" | "normal"
    and signals is a list of human-readable reasons contributing to it.
    """
    condition = (weather_condition or "").lower()
    raining = any(k in condition for k in ["rain", "drizzle", "thunderstorm"])

    flood_signals, drought_signals = [], []

    if soil_pct is not None:
        if soil_pct >= THRESHOLDS["flood_soil_min"]:
            flood_signals.append(f"Soil moisture very high ({soil_pct:.0f}%)")
        elif soil_pct <= THRESHOLDS["drought_soil_max"]:
            drought_signals.append(f"Soil moisture very low ({soil_pct:.0f}%)")

    if humidity_pct is not None:
        if humidity_pct >= THRESHOLDS["flood_humidity_min"]:
            flood_signals.append(f"Humidity very high ({humidity_pct:.0f}%)")
        elif humidity_pct <= THRESHOLDS["drought_humidity_max"]:
            drought_signals.append(f"Humidity very low ({humidity_pct:.0f}%)")

    if water_level_pct is not None and water_level_pct >= THRESHOLDS["flood_water_level_min"]:
        flood_signals.append(f"Water-level sensor high ({water_level_pct:.0f}%)")

    if raining:
        flood_signals.append(f"Current weather: {weather_condition}")
    elif condition:
        drought_signals.append(f"No rain in current conditions ({weather_condition})")

    if len(flood_signals) >= MIN_SIGNALS_FOR_ALERT:
        return "flood", flood_signals
    elif len(drought_signals) >= MIN_SIGNALS_FOR_ALERT:
        return "drought", drought_signals
    else:
        return "normal", (flood_signals + drought_signals) or ["All readings within normal range."]
