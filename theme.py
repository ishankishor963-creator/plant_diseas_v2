"""Shared AgriPulse-style glassmorphism theme, used on every page so the app
feels like one product instead of five separate scripts."""

import streamlit as st

BASE_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@500;600&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">

<style>
:root {
    --bg: #111410;
    --accent: #7DBE6F;
    --accent-2: #a1d494;
    --glow: rgba(125,190,111,0.22);
    --sky-tint: #E0F2F1;
    --harvest-gold: #F2C94C;
    --soil-brown: #4B3621;
    --secondary: #e9c349;
    --text: #e2e3dc;
    --text-muted: #c2c9bb;
    --border: rgba(224,242,241,0.15);
    --surface-highest: #333631;
    --error: #ffb4ab;
    --error-glow: rgba(255,180,171,0.35);
    --flood: #8ED1E8;
    --drought: #F2C94C;
    transition: background-color 0.8s ease;
}

#MainMenu, footer, header { visibility: hidden; }

.material-symbols-outlined {
    font-family: 'Material Symbols Outlined';
    font-weight: normal; font-style: normal; vertical-align: middle;
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

.stApp {
    background:
        linear-gradient(to bottom, rgba(17,20,16,0.4), transparent 40%, rgba(17,20,16,0.85)),
        radial-gradient(circle at top left, color-mix(in srgb, var(--accent) 14%, #14180F) 0%, var(--bg) 60%);
}
body, [class*="css"] { font-family: 'Hanken Grotesk', sans-serif; color: var(--text); }

[data-testid="stSidebar"] {
    background: rgba(15,18,14,0.92);
    border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebarNav"] li div a { border-radius: 8px; }
[data-testid="stSidebarNav"] li div a:hover { background: rgba(125,190,111,0.12); }

@keyframes fadeInUp { from { opacity:0; transform:translateY(14px);} to {opacity:1; transform:translateY(0);} }
@keyframes pulseGlow { 0%,100% {opacity:1;} 50% {opacity:0.55;} }
@keyframes scanSweep { 0% {left:-30%;} 100% {left:110%;} }
@keyframes growFill { from {width:0%;} }

.glass-card {
    background: rgba(255,255,255,0.045);
    backdrop-filter: blur(14px) saturate(150%);
    -webkit-backdrop-filter: blur(14px) saturate(150%);
    border: 1px solid var(--border);
    border-top: 1px solid rgba(255,255,255,0.25);
    border-radius: 16px;
    padding: 1.5rem 1.6rem;
    margin-bottom: 1.1rem;
    position: relative;
    overflow: hidden;
    animation: fadeInUp 0.45s ease both;
}

.app-header { display:flex; align-items:center; gap:0.5rem; padding:0.6rem 0 1.2rem 0; }
.app-header .material-symbols-outlined { color: var(--accent); font-size: 26px; }
.app-header h1 { font-size:1.5rem; font-weight:700; color:var(--accent); margin:0; }
.app-header .subtitle { color: var(--text-muted); font-size: 0.85rem; margin-left: 0.6rem; }

.label-mono {
    font-family:'JetBrains Mono',monospace; font-size:0.72rem; letter-spacing:0.08em;
    text-transform:uppercase; color:var(--text-muted); margin-bottom:0.6rem;
    display:flex; align-items:center; gap:0.4rem;
}
.label-mono .material-symbols-outlined { font-size:16px; color:var(--accent-2); }
.data-viz { font-family:'JetBrains Mono',monospace; font-weight:600; color:var(--text); }

.hero-temp { font-size:2.6rem; font-weight:700; color:#fff; line-height:1.1; margin:0; }
.hero-condition { font-size:1.15rem; font-weight:600; color:var(--text-muted); margin-left:0.6rem; }
.hero-desc-text { color:var(--text-muted); font-size:0.95rem; margin-top:0.5rem; max-width:32rem; line-height:1.5; }

.metric-tile { min-height:128px; display:flex; flex-direction:column; justify-content:space-between; }
.metric-value { font-size:1.5rem; font-weight:700; color:var(--text); margin:0.4rem 0; }
.progress-track { width:100%; height:8px; background:var(--surface-highest); border-radius:999px; overflow:hidden; border:1px solid var(--border); }
.progress-fill { height:100%; border-radius:999px; animation:growFill 1s cubic-bezier(0.22,1,0.36,1) both; }

.result-title { font-size:1.6rem; font-weight:700; color:#fff; margin:0 0 1rem 0; }

.rec-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.9rem; margin-top:0.3rem; }
@media (max-width:640px) { .rec-grid { grid-template-columns:1fr; } }
.rec-tile { padding:1rem 1.1rem; border-radius:12px; background:rgba(255,255,255,0.03); border:1px solid var(--border); border-left:3px solid var(--accent); }
.rec-tile.treatment { border-left-color:var(--accent-2); }
.rec-tile h4 { font-family:'JetBrains Mono',monospace; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--text-muted); margin:0 0 0.5rem 0; }
.rec-tile p { margin:0; font-size:0.92rem; line-height:1.5; color:var(--text); }

.unrecognized { border:1px solid var(--error-glow); background:rgba(255,180,171,0.06); border-radius:12px; padding:1rem 1.2rem; font-size:0.92rem; color:var(--text); }
.unrecognized-label { font-family:'JetBrains Mono',monospace; font-size:0.7rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--error); margin-bottom:0.5rem; font-weight:600; }

.alert-banner { border-radius:16px; padding:1.4rem 1.6rem; margin-bottom:1.1rem; border:1px solid; }
.alert-banner.flood { background:rgba(142,209,232,0.08); border-color:rgba(142,209,232,0.4); }
.alert-banner.drought { background:rgba(242,201,76,0.08); border-color:rgba(242,201,76,0.4); }
.alert-banner.normal { background:rgba(125,190,111,0.08); border-color:rgba(125,190,111,0.35); }
.alert-title { font-size:1.4rem; font-weight:700; margin:0 0 0.3rem 0; }
.alert-banner.flood .alert-title { color:var(--flood); }
.alert-banner.drought .alert-title { color:var(--drought); }
.alert-banner.normal .alert-title { color:var(--accent-2); }
.alert-signal { font-size:0.88rem; color:var(--text-muted); margin:0.15rem 0; }

.scan-track { position:relative; width:100%; height:3px; background:var(--surface-highest); border-radius:2px; overflow:hidden; margin:0.9rem 0 1rem 0; }
.scan-bar { position:absolute; top:0; height:100%; width:30%; background:linear-gradient(90deg,transparent,var(--accent),transparent); animation:scanSweep 1.3s linear infinite; }
.scan-line { font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:var(--text-muted); margin:0.3rem 0; animation:pulseGlow 1.6s ease-in-out infinite; }
.scan-line span { color:var(--accent-2); }

[data-testid="stFileUploader"] section { border:2px dashed rgba(125,190,111,0.4); border-radius:14px; background:rgba(255,255,255,0.03); }
[data-testid="stFileUploader"] label p { color:var(--text-muted) !important; }
[data-testid="stCameraInput"] video, [data-testid="stCameraInput"] img { border-radius:14px; border:1px solid var(--border); }

.stTabs [data-baseweb="tab-list"] { gap:0.4rem; }
.stTabs [data-baseweb="tab"] { background:rgba(255,255,255,0.04); border:1px solid var(--border); border-radius:10px 10px 0 0; color:var(--text-muted); font-family:'JetBrains Mono',monospace; font-size:0.78rem; letter-spacing:0.05em; }
.stTabs [aria-selected="true"] { color:var(--accent-2) !important; }

.loc-wrap input { background:rgba(255,255,255,0.05) !important; border:1px solid var(--border) !important; color:var(--text) !important; border-radius:10px !important; }

.web-link-title { color:var(--accent-2); font-weight:600; text-decoration:none; font-size:0.95rem; }
.web-link-body { margin:0.3rem 0 0 0; font-size:0.85rem; color:var(--text-muted); line-height:1.5; }

.sys-footer { font-family:'JetBrains Mono',monospace; font-size:0.68rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--text-muted); text-align:center; padding:1.2rem 0 0.5rem 0; border-top:1px solid var(--border); margin-top:0.5rem; }

@keyframes mirrorSheen { 0% {transform:translateX(-120%) rotate(8deg); opacity:0;} 15% {opacity:0.55;} 50% {opacity:0.35;} 100% {transform:translateX(120%) rotate(8deg); opacity:0;} }
@keyframes rainFall { from {transform:translateY(-10vh);} to {transform:translateY(110vh);} }
.rain-mode .glass-card { backdrop-filter:blur(18px) saturate(165%); -webkit-backdrop-filter:blur(18px) saturate(165%); background:linear-gradient(160deg,rgba(255,255,255,0.07),rgba(142,209,232,0.03) 60%); border-top:1px solid rgba(224,242,241,0.4); }
.rain-mode .glass-card::before { content:""; position:absolute; top:0; left:0; width:45%; height:220%; background:linear-gradient(100deg,transparent 30%,rgba(255,255,255,0.22) 48%,rgba(255,255,255,0.05) 55%,transparent 70%); animation:mirrorSheen 6s ease-in-out infinite; pointer-events:none; }
.weather-overlay { position:fixed; top:0; left:0; width:100%; height:100%; overflow:hidden; pointer-events:none; z-index:-1; }
.raindrop { position:absolute; top:-10%; width:1.5px; background:linear-gradient(to bottom,transparent,var(--accent),rgba(255,255,255,0.7)); animation-name:rainFall; animation-timing-function:linear; animation-iteration-count:infinite; opacity:0.55; }
.lightning-flash { position:fixed; top:0; left:0; width:100%; height:100%; background:#fff; opacity:0; animation:flash 7s infinite; pointer-events:none; z-index:999; }
@keyframes flash { 0%,95%,100% {opacity:0;} 96% {opacity:0.5;} 97% {opacity:0;} 98% {opacity:0.28;} }

@keyframes rayRotate { from {transform:rotate(0deg);} to {transform:rotate(360deg);} }
@keyframes sunPulse { 0%,100% {opacity:0.7;} 50% {opacity:1;} }
.sun-rays { position:absolute; top:50%; left:50%; width:220%; height:220%; transform:translate(-50%,-50%); background:repeating-conic-gradient(from 0deg,rgba(242,201,76,0.16) 0deg 6deg,transparent 6deg 24deg); animation:rayRotate 60s linear infinite; -webkit-mask-image:radial-gradient(circle,black 35%,transparent 70%); mask-image:radial-gradient(circle,black 35%,transparent 70%); }
.sun-glow { position:absolute; top:-25%; right:-15%; width:65vw; height:65vw; border-radius:50%; background:radial-gradient(circle,rgba(242,201,76,0.32) 0%,transparent 70%); animation:sunPulse 4s ease-in-out infinite; }

@keyframes snowFall { from {transform:translate(0,-10vh);} to {transform:translate(24px,110vh);} }
.snowflake { position:absolute; top:-5%; border-radius:50%; background:var(--accent); opacity:0.8; animation-name:snowFall; animation-timing-function:linear; animation-iteration-count:infinite; }

@keyframes cloudDrift { from {transform:translateX(-25vw);} to {transform:translateX(125vw);} }
.cloud-blob { position:absolute; border-radius:50%; filter:blur(30px); animation-name:cloudDrift; animation-timing-function:linear; animation-iteration-count:infinite; }
</style>
"""


def apply_theme():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def render_header(title, icon, subtitle=None):
    subtitle_html = f'<span class="subtitle">{subtitle}</span>' if subtitle else ""
    st.markdown(f"""
    <div class="app-header">
        <span class="material-symbols-outlined">{icon}</span>
        <h1>{title}</h1>
        {subtitle_html}
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown('<div class="sys-footer">Agro Edge // Crop Intelligence System // Team Cyberpunk</div>',
                unsafe_allow_html=True)


def gauge_color(pct):
    if pct >= 85:
        return "#7DBE6F"
    elif pct >= 70:
        return "#F2C94C"
    else:
        return "#ffb4ab"
