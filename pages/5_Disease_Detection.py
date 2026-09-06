import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(page_title="AI Disease Detection", page_icon="🔬", layout="wide")
st.title("🔬 AI Disease Detection")
st.caption(
    "Upload a leaf photo or capture one with your camera. Runs your "
    "existing MobileNetV2 model from the plant_disease_modal project."
)

MODEL_PATH = "model/plant_model_v5.keras"  # your trained model
CLASS_NAMES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Citrus_Canker",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Orange___Multiple_Diseases",
    "Orange___Nutrient_Deficiency",
    "Orange___healthy",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___Bacterial_Pustule",
    "Soybean___Brown_Spot",
    "Soybean___Crestamento",
    "Soybean___Ferrugen",
    "Soybean___Frogeye_Leaf_Spot",
    "Soybean___Mosaic_Virus",
    "Soybean___Powdery_Mildew",
    "Soybean___Rust",
    "Soybean___Septoria",
    "Soybean___Southern_Blight",
    "Soybean___Sudden_Death_Syndrome",
    "Soybean___Target_Leaf_Spot",
    "Soybean___Yellow_Mosaic",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]


@st.cache_resource
def load_model():
    try:
        import tensorflow as tf
        return tf.keras.models.load_model(MODEL_PATH)
    except Exception as e:
        st.session_state["model_load_error"] = str(e)
        return None


def predict(image: Image.Image, model):
    img = image.convert("RGB").resize((224, 224))
    arr = np.asarray(img) / 255.0
    arr = np.expand_dims(arr, axis=0)
    preds = model.predict(arr, verbose=0)[0]
    top_idx = int(np.argmax(preds))
    label = CLASS_NAMES[top_idx] if top_idx < len(CLASS_NAMES) else f"class_{top_idx}"
    confidence = float(preds[top_idx])
    return label, confidence


model = load_model()
if model is None:
    real_error = st.session_state.get("model_load_error", "Unknown error")
    st.warning(
        f"Couldn't load the model at `model/plant_model_v5.keras`.\n\n"
        f"**Actual error:** `{real_error}`\n\n"
        "The page still works below for testing the upload/camera flow.",
        icon="⚠️",
    )

st.divider()
tab_upload, tab_camera = st.tabs(["📁 Upload File", "📷 Use Camera"])

image_to_predict = None

with tab_upload:
    uploaded = st.file_uploader("Upload a leaf photo", type=["jpg", "jpeg", "png"])
    if uploaded:
        image_to_predict = Image.open(uploaded)
        st.image(image_to_predict, caption="Uploaded image", width=400)

with tab_camera:
    captured = st.camera_input("Take a photo of the leaf")
    if captured:
        image_to_predict = Image.open(captured)

if image_to_predict and st.button("🔍 Detect Disease", type="primary"):
    if model is None:
        st.error("Add your model file to `model/` first (see warning above).")
    else:
        with st.spinner("Analyzing..."):
            label, confidence = predict(image_to_predict, model)
        st.success(f"**Prediction:** {label}  \n**Confidence:** {confidence:.1%}")
