import streamlit as st

from utils.ai_agent import ai_reply
from utils.theme import inject_theme, topnav
from utils.auth import logout_button

inject_theme()
with st.sidebar:
    logout_button()
topnav("ai")

st.title("🤖 AI Assistant")
st.caption(
    "Ask about watering, pests, disease, weather risk, or fertilizer. "
    "Running on a built-in FAQ until an LLM API key is added — see "
    "utils/ai_agent.py for how to turn that on."
)

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

question = st.chat_input("Ask a question about your crops or field...")
if question:
    st.session_state["chat_history"].append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    answer = ai_reply(question, history=st.session_state["chat_history"][:-1])

    st.session_state["chat_history"].append({"role": "assistant", "content": answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

if st.session_state["chat_history"]:
    if st.button("Clear conversation"):
        st.session_state["chat_history"] = []
        st.rerun()
