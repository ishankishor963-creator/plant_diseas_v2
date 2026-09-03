"""Shared AI plant-disease diagnosis pipeline — used by the Home page
(upload / camera-input) and by the Live Camera page (on-demand diagnosis
from a captured frame), so the model is only loaded once and the logic
lives in exactly one place."""

import os

import numpy as np
import streamlit as st
import tensorflow as tf

# Class names must be in the same order the model was trained on.
# v5 combines the original 38-class PlantVillage set with a 2nd dataset
# adding Orange disease variants and 13 new Soybean diseases — 55 classes
# total, confirmed against the training notebook's train_ds.class_names.
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

SUPPORTED_CROPS = ("apple, blueberry, cherry, corn, grape, orange, peach, pepper, "
                   "potato, raspberry, soybean, squash, strawberry, tomato")

MODEL_PATH = "plant_model_v5.keras"


def get_class_display_name(index):
    """Safely map a predicted index to a class name, even if it falls outside
    the currently-named list (e.g. v5's classes 38-54, not yet added)."""
    if 0 <= index < len(CLASS_NAMES):
        return CLASS_NAMES[index], True
    return f"class_{index}", False


@st.cache_resource(show_spinner="Loading diagnosis model...")
def load_model():
    if not os.path.exists(MODEL_PATH):
        st.error(
            f"Model file '{MODEL_PATH}' not found in the repo root. "
            "Add it to your GitHub repo (Git LFS is recommended if it's "
            "over 100MB, since GitHub blocks larger plain files)."
        )
        st.stop()
    return tf.keras.models.load_model(MODEL_PATH)


def run_diagnosis(pil_image):
    """Run the full preprocessing + prediction pipeline on a PIL image.

    Returns a dict with: index, class_key, is_named, confidence, display_name
    (display_name is None when the class isn't named yet).
    """
    model = load_model()
    image = pil_image.convert("RGB")
    img_resized = image.resize((224, 224))
    img_array = np.expand_dims(np.array(img_resized), axis=0)

    predictions = model.predict(img_array)
    predicted_index = int(np.argmax(predictions[0]))
    confidence = 100 * float(np.max(predictions[0]))
    predicted_class, is_named = get_class_display_name(predicted_index)

    display_name = None
    if is_named:
        display_name = predicted_class.replace("___", " - ").replace("__", " ").replace("_", " ")

    return {
        "index": predicted_index,
        "class_key": predicted_class,
        "is_named": is_named,
        "confidence": confidence,
        "display_name": display_name,
    }
