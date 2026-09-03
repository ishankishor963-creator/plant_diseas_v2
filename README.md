# Smart Farming Assistant — Streamlit App

Multi-page dashboard: AI assistant, sensor readings, flood/drought alerts,
camera feed, and AI disease detection.

## Structure
```
Home.py                                  <- landing page + device URL setup
pages/
  1_🤖_AI_Assistant.py                   <- chat with the FAQ bot
  2_🌡️_Sensor_Dashboard.py               <- soil moisture / humidity / temp
  3_🚨_Flood_Drought_Alerts.py           <- risk alerts + rainfall forecast
  4_📷_Camera_Feed.py                     <- live snapshot from field camera
  5_🔬_Disease_Detection.py               <- upload/camera -> disease model
utils/
  esp_client.py                          <- talks to your ESP32/Pi API
  ai_agent.py                            <- FAQ bot (+ optional LLM upgrade)
model/                                   <- put your trained .h5 model here
```

## Run locally
```bash
pip install -r requirements.txt
streamlit run Home.py
```

## Connect your ESP32 / Raspberry Pi
Your device should serve two HTTP routes (edit `utils/esp_client.py` if
your firmware uses different ones):

- `GET /data` → JSON: `{"soil_moisture": 42.5, "humidity": 61.2, "temperature": 27.8}`
- `GET /capture` → raw JPEG bytes from the camera

Once it's running, type its IP (e.g. `http://192.168.1.42`) into the
sidebar on the site. Until then, every page runs on demo data so you can
build and test the UI without hardware attached.

## Add your trained disease-detection model
Copy your `.h5` model into `model/plant_disease_model.h5`, and update the
`CLASS_NAMES` list at the top of `pages/5_🔬_Disease_Detection.py` to match
the class order your model was trained on.

## Add a real AI assistant later (optional)
Right now the AI Assistant page uses a free, built-in FAQ engine — no API
key needed. When you get an Anthropic API key:
1. In Streamlit Cloud: **Manage app → Settings → Secrets**, add:
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
2. Uncomment `anthropic` in `requirements.txt`.
3. Nothing else changes — `utils/ai_agent.py` already checks for the key
   and switches over automatically.

## Deploying to Streamlit Community Cloud
1. Push this folder to a GitHub repo.
2. On share.streamlit.io, point it at `Home.py` as the main file.
3. If you hit an "Error installing requirements" — check **Manage app →
   terminal** for the real pip error (often a version pin or a package
   needing `-headless` variant).
