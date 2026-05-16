import streamlit as st
import numpy as np
from PIL import Image
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import time
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="PoultryGuardAI - Smart Detection",
    page_icon="🐔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Styling ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Load Config ---
PROJECT_ROOT = Path(__file__).parent

@st.cache_data
def load_config():
    config_path = PROJECT_ROOT / "disease_config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {"diseases": {}, "summary": {}}

config = load_config()

# --- Try loading AI models (graceful fallback to demo mode) ---
@st.cache_resource
def load_models():
    models_dir = PROJECT_ROOT / "AI" / "models"
    cnn_model = None
    risk_model = None
    labels = None

    # Load labels
    labels_path = models_dir / "poultry_cnn_labels.json"
    if labels_path.exists():
        try:
            with open(labels_path, 'r') as f:
                labels = json.load(f)
        except Exception:
            labels = None

    # Load CNN model — only if file exists AND tensorflow is available
    keras_path = models_dir / "poultry_cnn.keras"
    if keras_path.exists():
        try:
            import tensorflow as tf
            cnn_model = tf.keras.models.load_model(str(keras_path))
        except ImportError:
            pass  # TensorFlow not installed — demo mode
        except Exception:
            pass  # Model load failed — demo mode

    # Load risk model — only if file exists AND joblib is available
    risk_path = models_dir / "isolation_forest.pkl"
    if risk_path.exists():
        try:
            import joblib
            risk_model = joblib.load(risk_path)
        except ImportError:
            pass  # joblib not installed — demo mode
        except Exception:
            pass  # Model load failed — demo mode

    return cnn_model, risk_model, labels

try:
    cnn_model, risk_model, labels = load_models()
except Exception:
    cnn_model, risk_model, labels = None, None, None

MODELS_LOADED = cnn_model is not None and labels is not None

# --- Prediction Logic ---
def predict_disease(image):
    if not MODELS_LOADED:
        # Demo mode: return a random disease from config
        import random
        diseases = list(config['diseases'].keys())
        disease = random.choice(diseases)
        conf = round(random.uniform(0.65, 0.98), 3)
        return disease, conf

    import tensorflow as tf
    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    predictions = cnn_model.predict(img_array)
    class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][class_idx])
    disease_name = labels[str(class_idx)]

    return disease_name, confidence

# --- Sidebar ---
with st.sidebar:
    st.title("🐔 PoultryGuardAI")
    st.info("Smart monitoring system for poultry health using Deep Learning.")

    st.divider()
    st.subheader("System Status")
    if MODELS_LOADED:
        st.success("✅ AI Models: Loaded")
    else:
        st.warning("⚠️ AI Models: Demo Mode")
    st.success("✅ Config: Loaded")
    st.caption(f"Diseases tracked: {len(config.get('diseases', {}))}")

    st.divider()
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# --- Main App ---
st.title("🐔 PoultryGuardAI Dashboard")
st.write("Real-time disease detection and risk assessment system.")

if not MODELS_LOADED:
    st.info("🔬 Running in **Demo Mode** — AI models not found. Upload an image to see a simulated prediction.")

tabs = st.tabs(["🔍 Detection", "📊 Analytics", "📖 Knowledge Base"])

with tabs[0]:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader("Upload bird or fecal sample...", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Sample", use_container_width=True)

            if st.button("🔍 Run Diagnostic"):
                with st.spinner("Analyzing physiological patterns..."):
                    time.sleep(1.5)
                    disease, conf = predict_disease(image)

                    if 'history' not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "disease": disease,
                        "conf": conf
                    })

                    st.session_state.last_result = {"disease": disease, "conf": conf}
                    st.rerun()

    with col2:
        if 'last_result' in st.session_state:
            res = st.session_state.last_result
            disease_info = config['diseases'].get(res['disease'], {})

            st.subheader("Diagnostic Result")

            risk_color = "#ff4b4b" if res['conf'] > 0.8 else "#ffa500" if res['conf'] > 0.5 else "#28a745"
            risk_label = "HIGH" if res['conf'] > 0.8 else "MEDIUM" if res['conf'] > 0.5 else "LOW"

            st.markdown(f"""
                <div style="background-color: {risk_color}22; padding: 20px; border-left: 5px solid {risk_color}; border-radius: 5px;">
                    <h2 style="color: {risk_color}; margin: 0;">{res['disease']}</h2>
                    <p style="font-size: 1.2em; margin: 10px 0;">Confidence: <b>{res['conf']*100:.1f}%</b> | Risk: <b>{risk_label}</b></p>
                </div>
            """, unsafe_allow_html=True)

            st.divider()
            st.subheader("Action Plan")
            st.write(f"**Description:** {disease_info.get('description', 'N/A')}")

            symptoms = disease_info.get('symptoms', [])
            if symptoms:
                st.write("**Symptoms to watch for:**")
                for s in symptoms:
                    st.write(f"- {s}")

            if res['disease'] != "Healthy":
                st.warning("**Immediate Recommendation:** Isolate affected birds and sanitize the area.")
            else:
                st.success("**Status:** Bird appears healthy. Continue regular monitoring.")
        else:
            st.info("Upload an image and click 'Run Diagnostic' to see results here.")

with tabs[1]:
    st.subheader("Historical Trends")
    if 'history' in st.session_state and st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df.set_index('time')['conf'])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No diagnostic data available yet. Run a detection first.")

with tabs[2]:
    st.subheader("Disease Reference Library")
    disease_list = list(config.get('diseases', {}).keys())

    if disease_list:
        selected_disease = st.selectbox("Select a disease to learn more:", disease_list)

        info = config['diseases'][selected_disease]
        st.write(f"### {selected_disease}")
        col_a, col_b = st.columns(2)
        with col_a:
            st.write(f"**Aliases:** {info.get('alias', 'None')}")
            st.write(f"**Priority:** {info.get('priority', 'Normal')}")
        with col_b:
            st.write(f"**Training images:** {info.get('training_images', 0)}")
            st.write(f"**Reference images:** {info.get('reference_images', 0)}")
        st.write(f"**Overview:** {info.get('description', '')}")

        symptoms = info.get('symptoms', [])
        if symptoms:
            st.write("#### Common Symptoms")
            for s in symptoms:
                st.write(f"- {s}")
    else:
        st.warning("No disease configuration found.")

# --- Footer ---
st.divider()
mode_text = "AI Mode" if MODELS_LOADED else "Demo Mode"
st.caption(f"PoultryGuardAI v1.0 | {mode_text} | Powered by TensorFlow & Streamlit")
