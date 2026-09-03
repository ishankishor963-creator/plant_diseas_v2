import streamlit as st

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from theme import apply_theme, render_header, render_footer

st.set_page_config(page_title="Ask the Plant AI — Agro Edge", page_icon="🤖", layout="centered")
apply_theme()
render_header("Ask the Plant AI", "smart_toy", "Your field agronomist, on call")

st.markdown("""
<div class="glass-card">
    <p class="hero-desc-text">
        Ask anything about the crop you're growing — symptoms, treatment options,
        watering schedules, or what today's diagnosis result means in practice.
    </p>
</div>
""", unsafe_allow_html=True)

SYSTEM_PROMPT = (
    "You are the in-app plant care assistant for Agro Edge, a crop-disease "
    "detection and field-monitoring system used by farmers. Give practical, "
    "concise agronomy advice: disease identification context, treatment and "
    "prevention steps, irrigation and soil guidance, and general crop care. "
    "Keep answers focused and actionable, use plain language, and ask a "
    "clarifying question if the crop or symptom described is ambiguous. "
    "You are not a substitute for a licensed agronomist or plant pathologist "
    "for high-stakes commercial decisions — say so if the situation calls for it."
)

if not ANTHROPIC_API_KEY:
    st.markdown("""
    <div class="glass-card">
        <div class="unrecognized">
            <div class="unrecognized-label">⚠ Not configured</div>
            Add <code>ANTHROPIC_API_KEY</code> to your app's <code>.streamlit/secrets.toml</code>
            to enable this agent.
        </div>
    </div>
    """, unsafe_allow_html=True)
    render_footer()
    st.stop()

try:
    import anthropic
except ModuleNotFoundError:
    st.error("The `anthropic` package isn't installed. Run: pip install anthropic")
    render_footer()
    st.stop()

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about your crop's symptoms, care, or treatment...")

if user_input:
    st.session_state.chat_messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        try:
            with client.messages.stream(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages],
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"Sorry, something went wrong reaching the AI agent: {e}"
            placeholder.markdown(full_response)

    st.session_state.chat_messages.append({"role": "assistant", "content": full_response})

render_footer()
