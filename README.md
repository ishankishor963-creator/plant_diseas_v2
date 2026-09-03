# Agro Edge

AI-powered crop-disease diagnosis and field-monitoring dashboard, built with
Streamlit.

## Structure

```
agro-edge/
├── app.py                     ← main page: AI leaf diagnosis (upload/camera)
├── config.py                  ← sensor channels, API keys, thresholds
├── theme.py                   ← shared CSS/theme
├── sensors.py                 ← ThingSpeak read helpers
├── weather_utils.py           ← OpenWeatherMap + flood/drought scoring
├── diagnosis.py                ← shared AI model-loading + prediction logic
├── requirements.txt
├── runtime.txt                ← pins Python 3.11 for TensorFlow compatibility
├── .streamlit/
│   └── secrets.toml.example   ← copy to secrets.toml and fill in real keys
└── pages/                     ← Streamlit auto-detects these as sidebar pages
    ├── 1_🎥_Live_Camera.py
    ├── 2_🌊_Flood_Drought_Alerts.py
    ├── 3_🌡️_Temperature_Humidity.py
    └── 4_🤖_Ask_AI_Agent.py
```

**You still need to add two files yourself** (not included here):
- `recommendations.py` — your `RECOMMENDATIONS` dict, imported by `app.py`
- `plant_model_v5.keras` — your trained model, loaded by `diagnosis.py`

Drop both into the repo root before deploying.

## Local setup

1. Clone this repo.
2. `pip install -r requirements.txt`
3. `cp .streamlit/secrets.toml.example .streamlit/secrets.toml` and fill in
   your real `OPENWEATHER_API_KEY` and `ANTHROPIC_API_KEY`.
4. Add your `recommendations.py` and `plant_model_v5.keras` to the repo root.
5. `streamlit run app.py`

## Deploying on Streamlit Community Cloud

1. Push this repo to GitHub (see checklist below).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app
   pointing at this repo, branch `main`, **main file path: `app.py`**.
3. In the app's Settings → Secrets, paste the same two keys from
   `secrets.toml.example` with your real values.
4. Deploy. Sidebar pages (Live Camera, Flood & Drought Alerts,
   Temperature & Humidity, Ask AI Agent) appear automatically because
   they live in `pages/`.

### Pre-push checklist (avoids the most common deploy failures)

- [ ] `app.py`, `requirements.txt`, and `runtime.txt` are all at the **repo
      root** — not nested in a subfolder.
- [ ] The **Main file path** in Streamlit Cloud's app settings says `app.py`
      exactly (not `Home.py` or the default `app.py` placeholder from an
      earlier version of the app).
- [ ] `recommendations.py` and `plant_model_v5.keras` are actually present in
      the repo. If `plant_model_v5.keras` is over 100MB, GitHub will reject a
      plain push — use [Git LFS](https://git-lfs.github.com/) for it.
- [ ] The four page files sit inside `pages/`, not the repo root.
- [ ] `requirements.txt` uses `tensorflow-cpu` (not `tensorflow`) and pins
      `numpy<2.2` — this avoids a known TensorFlow/numpy ABI mismatch that
      causes a segmentation fault (no Python traceback) on Streamlit Cloud's
      free tier.
- [ ] `runtime.txt` says `python-3.11` — newer Python versions can fail to
      resolve a compatible TensorFlow build.
- [ ] Real secrets are **never committed** — only `secrets.toml.example` goes
      in the repo; the real `secrets.toml` is git-ignored.

If the app still crashes after deploying, check **Manage app → logs** for the
actual traceback — the generic "Error running app" banner never shows the
real cause on its own.

## Wiring up your ESP32 boards

Open `config.py` and fill in `SENSOR_CHANNELS` for each sensor as its board
goes live — e.g. once your temperature/humidity ESP32 is pushing to a
ThingSpeak channel:
```python
"temperature": {"channel_id": "1234567", "read_api_key": "XXXX", "field": 1, "unit": "°C"},
"humidity":    {"channel_id": "1234567", "read_api_key": "XXXX", "field": 2, "unit": "%"},
```
(same channel, different fields, is the usual DHT/SHT sensor setup). The
soil moisture board is already wired to the existing channel `3467712`.

**LoRa nodes:** each field ESP32 talks LoRa to a single gateway (an ESP32 or
Raspberry Pi with a LoRa receiver); the gateway posts to ThingSpeak over
WiFi. This app only ever talks to ThingSpeak — it doesn't need to know about
LoRa at all.

**Camera board (ESP32-S3 + OV2640):** once deployed, it can serve an MJPEG
stream at something like `http://<device-ip>:81/stream`. Replace the webcam
block in `pages/1_🎥_Live_Camera.py` with an `st.image` loop reading that URL
— the diagnosis button below it doesn't need to change.

**Solar + battery + enclosure:** no code changes needed — every sensor page
already shows a graceful "not configured / no data" state instead of
crashing when a board is offline.
