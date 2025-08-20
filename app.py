import streamlit as st
import pandas as pd
import joblib
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="Network Intrusion Detection System", layout="wide")
st.title("🛡️ Real-Time Network Intrusion Detection System")
st.write("Upload a CSV file with network traffic data to classify it as normal or an attack.")


# --- Caching Assets for Performance ---
@st.cache_resource
def load_assets():
    """Loads all necessary pre-trained assets from disk."""
    try:
        model = joblib.load('ids_rf_model.pkl')
        scaler = joblib.load('scaler.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
        model_columns = joblib.load('model_columns.pkl')
        return model, scaler, label_encoder, model_columns
    except FileNotFoundError:
        st.error("Required model assets not found. Please ensure all .pkl files are present.")
        return None, None, None, None


# --- Load Assets ---
model, scaler, label_encoder, model_columns = load_assets()

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a CSV file from the CICIDS2017 dataset", type="csv")

if uploaded_file is not None and model is not None:
    try:
        df_test = pd.read_csv(uploaded_file)
        st.write("Uploaded Data Preview:")
        st.dataframe(df_test.head())

        # --- Preprocess Uploaded Data ---
        df_processed = df_test.copy()
        df_processed.columns = df_processed.columns.str.strip()
        df_processed.replace([np.inf, -np.inf], np.nan, inplace=True)
        df_processed.dropna(inplace=True)

        df_processed = df_processed.reindex(columns=model_columns, fill_value=0)

        X_test_scaled = scaler.transform(df_processed)

        # --- Make & Display Predictions ---
        predictions = model.predict(X_test_scaled)
        prediction_labels = label_encoder.inverse_transform(predictions)

        df_display = df_test.loc[df_processed.index].copy()
        df_display['Predicted Attack'] = prediction_labels

        st.write("---")
        st.header("Prediction Results")

        # Filter to only show rows predicted as attacks
        df_attacks = df_display[df_display['Predicted Attack'] != 'BENIGN']

        if df_attacks.empty:
            st.success("✅ No intrusions detected in the uploaded file.")
        else:
            st.warning(f"🚨 Found {len(df_attacks)} potential intrusions out of {len(df_display)} total records.")
            st.dataframe(df_attacks)

        # --- Display Summary ---
        st.header("Prediction Summary")
        attack_counts = df_display['Predicted Attack'].value_counts()
        st.bar_chart(attack_counts)
        st.write(attack_counts)

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")