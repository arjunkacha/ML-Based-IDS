import streamlit as st
from auth import require_login
import pandas as pd
import joblib
import numpy as np

# --- Page Configuration ---
st.set_page_config(page_title="File-Based IDS Analysis", layout="wide")
require_login()
st.title("📊 File-Based Analysis with Model Comparison")
st.write("Upload a CSV file to analyze its traffic using both Random Forest and XGBoost models.")


# --- Caching Assets for Performance ---
@st.cache_resource
def load_assets():
    """Loads all necessary pre-trained assets from disk."""
    try:
        rf_model = joblib.load('ids_rf_model.pkl')
        xgb_model = joblib.load('ids_xgb_model.pkl')  # Load the new XGBoost model
        scaler = joblib.load('scaler.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
        model_columns = joblib.load('model_columns.pkl')
        return rf_model, xgb_model, scaler, label_encoder, model_columns
    except FileNotFoundError as e:
        st.error(f"Required model asset not found: {e}. Please ensure all .pkl files are in the directory.")
        return None, None, None, None, None


# --- Load Assets ---
rf_model, xgb_model, scaler, label_encoder, model_columns = load_assets()

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a CSV file from the CICIDS2017 dataset", type="csv")

if uploaded_file is not None and all([rf_model, xgb_model, scaler]):
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

        # --- Make Predictions with BOTH Models ---
        rf_predictions = rf_model.predict(X_test_scaled)
        rf_prediction_labels = label_encoder.inverse_transform(rf_predictions)

        xgb_predictions = xgb_model.predict(X_test_scaled)
        xgb_prediction_labels = label_encoder.inverse_transform(xgb_predictions)

        # Also get prediction probabilities to surface suspicious rows
        try:
            rf_proba = rf_model.predict_proba(X_test_scaled)
            rf_classes = rf_model.classes_
            rf_mapped = label_encoder.inverse_transform(rf_classes)
            # compute max non-BENIGN probability per row
            if 'BENIGN' in rf_mapped:
                ben_idx = list(rf_mapped).index('BENIGN')
                other_idx = [i for i in range(len(rf_mapped)) if i != ben_idx]
                rf_max_nonbenign = rf_proba[:, other_idx].max(axis=1)
            else:
                rf_max_nonbenign = rf_proba.max(axis=1)
        except Exception:
            rf_max_nonbenign = np.zeros(X_test_scaled.shape[0])

        try:
            xgb_proba = xgb_model.predict_proba(X_test_scaled)
            xgb_classes = xgb_model.classes_
            xgb_mapped = label_encoder.inverse_transform(xgb_classes)
            if 'BENIGN' in xgb_mapped:
                ben_idx = list(xgb_mapped).index('BENIGN')
                other_idx = [i for i in range(len(xgb_mapped)) if i != ben_idx]
                xgb_max_nonbenign = xgb_proba[:, other_idx].max(axis=1)
            else:
                xgb_max_nonbenign = xgb_proba.max(axis=1)
        except Exception:
            xgb_max_nonbenign = np.zeros(X_test_scaled.shape[0])

        # Add predictions to the original dataframe for display
        df_display = df_test.loc[df_processed.index].copy()
        df_display['RF_Prediction'] = rf_prediction_labels
        df_display['XGB_Prediction'] = xgb_prediction_labels

        st.write("---")
        st.header("Prediction Results")

        # Suspicion threshold (show rows with high non-BENIGN probability even if predicted BENIGN)
        # threshold = st.sidebar.slider('Suspicion probability threshold', min_value=0.0, max_value=1.0, value=0.2, step=0.01)

        df_display['RF_Max_NonBenign_Prob'] = rf_max_nonbenign
        df_display['XGB_Max_NonBenign_Prob'] = xgb_max_nonbenign

        # Filter to show rows where AT LEAST ONE model detected an attack OR probability exceeds threshold
        df_attacks = df_display[
            (df_display['RF_Prediction'] != 'BENIGN') |
            (df_display['XGB_Prediction'] != 'BENIGN')
            # (df_display['RF_Max_NonBenign_Prob'] > threshold) |
            # (df_display['XGB_Max_NonBenign_Prob'] > threshold)
        ]

        if df_attacks.empty:
            st.success("✅ No intrusions detected by either model using current threshold.")
            # show top suspicion rows by RF probability for debugging
            top_suspicious = df_display.sort_values('RF_Max_NonBenign_Prob', ascending=False).head(5)
            st.subheader('Top suspicious rows (by RF non-BENIGN probability)')
            st.dataframe(top_suspicious[['RF_Max_NonBenign_Prob','XGB_Max_NonBenign_Prob'] + list(top_suspicious.columns[:5])])
        else:
            st.warning(f"🚨 Found {len(df_attacks)} potential intrusions out of {len(df_display)} total records.")
            st.dataframe(df_attacks)

        # --- Display Summary ---
        st.header("Prediction Summary")
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Random Forest Predictions")
            rf_counts = df_display['RF_Prediction'].value_counts()
            st.bar_chart(rf_counts)
            st.write(rf_counts)

        with col2:
            st.subheader("XGBoost Predictions")
            xgb_counts = df_display['XGB_Prediction'].value_counts()
            st.bar_chart(xgb_counts)
            st.write(xgb_counts)

    except Exception as e:
        st.error(f"An error occurred during processing: {e}")