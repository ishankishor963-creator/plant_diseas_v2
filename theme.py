"""
theme.py
--------
Shared "field telemetry" dark theme for the Smart Farming Assistant.

Call inject_theme() once at the top of a page, then use stat_card()
for a single glowing metric tile (Sensor Dashboard) or
feature_card_header() + st.page_link() for a Home page tile.

Each gradient is tied to what the metric actually represents (soil,
water, heat) rather than one repeated gradient reused on every card.
"""

import streamlit as st

GRADIENTS = {
    "soil_moisture": "linear-gradient(135deg, #0B4F45 0%, #7ED957 100%)",
    "humidity": "linear-gradient(135deg, #173A5E 0%, #4FD1E8 100%)",
    "temperature": "linear-gradient(135deg, #5C1A1A 0%, #F2A65A 100%)",
    "ai_assistant": "linear-gradient(135deg, #3A2A12 0%, #C97A2B 100%)",
    "sensor_dashboard": "linear-gradient(135deg, #0F3D33 0%, #2FA98C 100%)",
    "alerts": "linear-gradient(135deg, #2A2E38 0%, #D9534F 100%)",
    "camera_feed": "linear-gradient(135deg, #1B1F3B 0%, #E8724C 100%)",
    "disease_detection": "linear-gradient(135deg, #16301F 0%, #6FBF73 100%)",
}

GLOW = {
    "soil_moisture": "rgba(126, 217, 87, 0.25)",
    "humidity": "rgba(79, 209, 232, 0.25)",
    "temperature": "rgba(242, 166, 90, 0.28)",
    "ai_assistant": "rgba(201, 122, 43, 0.28)",
    "sensor_dashboard": "rgba(47, 169, 140, 0.28)",
    "alerts": "rgba(217, 83, 79, 0.30)",
    "camera_feed": "rgba(232, 114, 76, 0.28)",
    "disease_detection": "rgba(111, 191, 115, 0.28)",
}


def inject_theme():
    """Dark background + typography. Call at the top of every page that
    should carry the theme — Streamlit reruns each page script fresh,
    so this doesn't automatically carry over to pages that don't call it."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&display=swap');

        [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background: #0D1512;
        }
        [data-testid="stSidebar"] {
            background: #0A100D;
            border-right: 1px solid #1E2C24;
        }
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0);
        }
        h1, h2, h3 {
            font-family: 'Space Grotesk', sans-serif;
            color: #F3F8F5 !important;
            letter-spacing: -0.01em;
        }
        p, span, label, div, .stMarkdown {
            color: #CBD8D0;
        }
        [data-testid="stCaptionContainer"] { color: #8CA096 !important; }

        /* --- Stat tile (Sensor Dashboard) --- */
        .tc-stat {
            border-radius: 18px;
            padding: 1.4rem 1.5rem;
            margin-bottom: 0.6rem;
        }
        .tc-stat .tc-icon { font-size: 1.4rem; opacity: 0.9; }
        .tc-stat .tc-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.1rem;
            font-weight: 700;
            color: #FFFFFF;
            line-height: 1.1;
            margin-top: 0.35rem;
        }
        .tc-stat .tc-unit { font-size: 1.1rem; font-weight: 500; opacity: 0.85; margin-left: 2px; }
        .tc-stat .tc-label {
            font-size: 0.92rem;
            color: rgba(255,255,255,0.85);
            margin-top: 0.15rem;
        }

        /* --- Feature tile (Home) --- */
        .tc-feature {
            border-radius: 18px 18px 0 0;
            padding: 1.4rem 1.5rem 1rem 1.5rem;
        }
        .tc-feature .tc-icon { font-size: 1.6rem; }
        .tc-feature .tc-title {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.15rem;
            font-weight: 600;
            color: #FFFFFF;
            margin-top: 0.5rem;
        }
        .tc-feature .tc-desc {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.85);
            margin-top: 0.3rem;
            line-height: 1.4;
        }

        /* Fuse the st.page_link that follows a .tc-feature into the
           same visual card, flush against its bottom edge. */
        div[data-testid="stPageLink"] {
            background: #0F1713;
            border: 1px solid rgba(255,255,255,0.08);
            border-top: none;
            border-radius: 0 0 18px 18px !important;
            padding: 0.55rem 1rem !important;
            margin-top: -0.6rem;
        }
        div[data-testid="stPageLink"] p {
            color: #E9F2EC !important;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def stat_card(key: str, icon: str, label: str, value, unit: str = ""):
    st.markdown(
        f"""
        <div class="tc-stat" style="background:{GRADIENTS[key]};
             box-shadow: 0 12px 28px -8px {GLOW[key]};">
            <div class="tc-icon">{icon}</div>
            <div class="tc-value">{value}<span class="tc-unit">{unit}</span></div>
            <div class="tc-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card_header(key: str, icon: str, title: str, desc: str):
    """Renders the gradient top of a feature card. Follow immediately
    with st.page_link(...) — the CSS above fuses the two into one card."""
    st.markdown(
        f"""
        <div class="tc-feature" style="background:{GRADIENTS[key]};
             box-shadow: 0 14px 30px -10px {GLOW[key]};">
            <div class="tc-icon">{icon}</div>
            <div class="tc-title">{title}</div>
            <div class="tc-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
