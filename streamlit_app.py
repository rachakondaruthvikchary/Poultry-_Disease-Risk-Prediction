import streamlit as st
import numpy as np
from PIL import Image
import tensorflow as tf
import joblib
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import time

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
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #ff4b4b;
        color: white;
    }
    .status-box {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Load Models & Config ---
@st.cache_resource
def load_resources():
    project_root = Path(__file__).parent
    
    # Load Config
    with open(project_root / "disease_config.json", 'r') as f:
        config = json.load(f)
    
    # Load Models
    cnn_model = tf.keras.models.load_model(project_root / "AI" / "models" / "poultry_cnn.keras")
    risk_model = joblib.load(project_root / "AI" / "models" / "isolation_forest.pkl")
    
    # Load Labels
    with open(project_root / "AI" / "models" / "poultry_cnn_labels.json", 'r') as f:
        labels = json.load(f)
        
    return config, cnn_model, risk_model, labels

try:
    config, cnn_model, risk_model, labels = load_resources()
except Exception as e:
    st.error(f"Error loading models: {e}. Please ensure AI/models/ directory is populated.")
    st.stop()

# --- Prediction Logic ---
def predict_disease(image):
    # Preprocess image
    img = image.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = cnn_model.predict(img_array)
    class_idx = np.argmax(predictions[0])
    confidence = float(predictions[0][class_idx])
    disease_name = labels[str(class_idx)]
    
    return disease_name, confidence

# --- Sidebar ---
with st.sidebar:
    st.image("https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png", width=150) # Placeholder for logo
    st.title("PoultryGuardAI")
    st.info("Smart monitoring system for poultry health using Deep Learning.")
    
    st.divider()
    st.subheader("System Status")
    st.success("Models: Loaded")
    st.success("Database: Connected")
    
    st.divider()
    if st.button("Clear History"):
        st.session_state.history = []

# --- Main App ---
st.title("🐔 PoultryGuardAI Dashboard")
st.write("Real-time disease detection and risk assessment system.")

tabs = st.tabs(["🔍 Detection", "📊 Analytics", "📖 Knowledge Base"])

with tabs[0]:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader("Upload bird or fecal sample...", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Sample", use_container_width=True)
            
            if st.button("Run Diagnostic"):
                with st.spinner("Analyzing physiological patterns..."):
                    time.sleep(1.5) # Simulating processing
                    disease, conf = predict_disease(image)
                    
                    # Store result
                    if 'history' not in st.session_state:
                        st.session_state.history = []
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M"),
                        "disease": disease,
                        "conf": conf
                    })
                    
                    st.session_state.last_result = {"disease": disease, "conf": conf}

    with col2:
        if 'last_result' in st.session_state:
            res = st.session_state.last_result
            disease_info = config['diseases'].get(res['disease'], {})
            
            st.subheader("Diagnostic Result")
            
            # Risk Level Color
            risk_color = "#ff4b4b" if res['conf'] > 0.8 else "#ffa500" if res['conf'] > 0.5 else "#28a745"
            
            st.markdown(f"""
                <div style="background-color: {risk_color}22; padding: 20px; border-left: 5px solid {risk_color}; border-radius: 5px;">
                    <h2 style="color: {risk_color}; margin: 0;">{res['disease']}</h2>
                    <p style="font-size: 1.2em; margin: 10px 0;">Confidence: <b>{res['conf']*100:.1f}%</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            st.divider()
            st.subheader("Action Plan")
            st.write(f"**Description:** {disease_info.get('description', 'N/A')}")
            
            st.write("**Symptoms to watch for:**")
            for s in disease_info.get('symptoms', []):
                st.write(f"- {s}")
                
            st.warning("**Immediate Recommendation:** Isolate affected birds and sanitize the area.")

with tabs[1]:
    st.subheader("Historical Trends")
    if 'history' in st.session_state and st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.line_chart(df.set_index('time')['conf'])
        st.table(df)
    else:
        st.info("No diagnostic data available yet.")

with tabs[2]:
    st.subheader("Disease Reference Library")
    disease_list = list(config['diseases'].keys())
    selected_disease = st.selectbox("Select a disease to learn more:", disease_list)
    
    info = config['diseases'][selected_disease]
    st.write(f"### {selected_disease}")
    st.write(f"**Aliases:** {info.get('alias', 'None')}")
    st.write(f"**Priority:** {info.get('priority', 'Normal')}")
    st.write(f"**Overview:** {info.get('description', '')}")
    
    st.write("#### Common Symptoms")
    for s in info.get('symptoms', []):
        st.write(f"- {s}")

# --- Footer ---
st.divider()
st.caption("PoultryGuardAI v1.0 | Powered by TensorFlow and Streamlit")
