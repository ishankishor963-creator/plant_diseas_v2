import numpy as np
import streamlit as st
from PIL import Image

st.set_page_config(page_title="AI Disease Detection", page_icon="🔬", layout="wide")
st.title("🔬 AI Disease Detection")
st.caption(
    "Upload a leaf photo or capture one with your camera. Runs your "
    "existing MobileNetV2 model from the plant_disease_modal project."
)

MODEL_PATH = "model/plant_disease_model.h5"  # copy your trained model here
# TODO: replace with your real class list (38 classes from PlantVillage
# in your original project) in the same order the model was trained on.
CLASS_NAMES = ["Class_0_placeholder", "Class_1_placeholder", "..."]


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
    st.warning(
        "Model file not found at `model/plant_disease_model.h5`. Copy your "
        "trained model into the `model/` folder (and fill in `CLASS_NAMES` "
        "at the top of this file) to activate real predictions. The page "
        "still works below for testing the upload/camera flow.",
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
