"""
ai_agent.py
-----------
Answers customer/farmer questions.

You said you don't have an LLM API key yet, so this ships with a
rule-based FAQ engine (keyword matching over common farming topics) —
it works immediately, no signup, no cost.

WHEN YOU GET AN API KEY LATER:
Set ANTHROPIC_API_KEY in Streamlit's secrets (Manage app -> Settings ->
Secrets), then call `ai_reply()` instead of `rule_based_reply()` in
pages/1_AI_Assistant.py. The function is already written below —
it just needs `anthropic` added to requirements.txt and a key in
st.secrets to activate. Anthropic has a free trial credit for new
accounts if you want to try it: https://console.anthropic.com/
"""

import streamlit as st

# ---------------------------------------------------------------------
# 1) Rule-based fallback (works today, no key needed)
# ---------------------------------------------------------------------

FAQ_RULES = [
    (["water", "irrigat", "moisture"],
     "Most crops do best with soil moisture between 40-60%. Check the "
     "Sensor Dashboard page for your live reading — if it's below 30%, "
     "irrigation is usually recommended (unless heavy rain is forecast; "
     "see the Flood/Drought Alerts page)."),
    (["pest", "insect", "bug"],
     "For pest issues, upload a photo of the affected leaf on the AI "
     "Model page — the disease/pest detector will identify it and "
     "suggest treatment. In general, neem-oil based sprays are a safe "
     "first line of defense for most common pests."),
    (["disease", "spot", "leaf", "fungus", "blight", "rot"],
     "Head to the AI Model page and upload (or capture) a photo of the "
     "affected leaf — the model will classify the disease and give "
     "treatment guidance."),
    (["flood", "heavy rain", "waterlog"],
     "Check the Flood/Drought Alerts page — it combines your live soil "
     "moisture reading with the rainfall forecast to warn you before "
     "waterlogging becomes a risk."),
    (["drought", "dry", "no rain"],
     "The Flood/Drought Alerts page tracks soil moisture trends and "
     "rainfall forecasts together, and will flag a drought risk before "
     "your soil crosses a critical threshold."),
    (["temperature", "heat", "hot", "cold"],
     "Check the Sensor Dashboard page for the live temperature reading. "
     "Most staple crops are stressed above 35°C or below 10°C — shading "
     "or mulching can help buffer extreme heat."),
    (["camera", "cctv", "watch", "monitor field"],
     "The Camera Feed page shows a live snapshot from your connected "
     "field camera — use the refresh button to pull the latest frame."),
    (["fertiliz", "nutrient", "npk"],
     "Nutrient deficiency often shows first as leaf discoloration. "
     "Upload a leaf photo on the AI Model page — the model flags "
     "nutrient-deficiency patterns alongside disease."),
]

DEFAULT_REPLY = (
    "I'm currently running on a built-in FAQ (no AI model key is set up "
    "yet), so I can help with: watering/irrigation, pests, plant disease, "
    "flood/drought risk, temperature, fertilizer, and the camera feed. "
    "Try asking about one of those, or check the relevant page in the "
    "sidebar."
)


def rule_based_reply(question: str) -> str:
    q = question.lower()
    for keywords, answer in FAQ_RULES:
        if any(kw in q for kw in keywords):
            return answer
    return DEFAULT_REPLY


# ---------------------------------------------------------------------
# 2) Real LLM path (activate once you have an API key)
# ---------------------------------------------------------------------

def ai_reply(question: str, history: list[dict] | None = None) -> str:
    """
    Calls Claude to answer the question, with the FAQ reply as a fallback
    if no API key is configured or the call fails. `history` is an
    optional list of {"role": "user"/"assistant", "content": str} for
    multi-turn context.
    """
    api_key = st.secrets.get("ANTHROPIC_API_KEY", None)
    if not api_key:
        return rule_based_reply(question)

    try:
        import anthropic  # requires `anthropic` in requirements.txt

        client = anthropic.Anthropic(api_key=api_key)
        messages = (history or []) + [{"role": "user", "content": question}]
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=500,
            system=(
                "You are a helpful farming assistant embedded in a smart "
                "farming dashboard. Answer concisely and practically for "
                "a farmer using soil moisture, humidity/temperature "
                "sensors, and a plant-disease camera model."
            ),
            messages=messages,
        )
        return "".join(
            block.text for block in response.content if block.type == "text"
        )
    except Exception:
        return rule_based_reply(question)
