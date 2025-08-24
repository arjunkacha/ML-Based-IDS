import streamlit as st
import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import os

st.set_page_config(page_title="Model Performance", layout="wide")
st.title("📊 Model Performance & Alert Log")
st.write("This page shows the performance of the trained Random Forest model and a historical log of all detected alerts.")

# --- Define Log File ---
ALERT_LOG_FILE = "alert_log.csv"

# --- Caching to load data and model only once ---
@st.cache_resource
def load_assets_for_evaluation():
    try:
        _, X_test, _, y_test = joblib.load('train_test_data.pkl')
        model = joblib.load('ids_rf_model.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
        return X_test, y_test, model, label_encoder
    except FileNotFoundError:
        st.error("Could not find necessary .pkl files. Please run the training scripts first.")
        return None, None, None, None

# --- Load data ---
X_test, y_test, model, label_encoder = load_assets_for_evaluation()

if model is not None:
    y_pred = model.predict(X_test)
    class_names = label_encoder.classes_

    st.header("Classification Report")
    report = classification_report(y_test, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    df_report = pd.DataFrame(report).transpose()
    st.dataframe(df_report)
    
    st.header("Confusion Matrix")
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names, ax=ax)
    plt.title('Confusion Matrix for the Random Forest Model')
    plt.ylabel('Actual Label')
    plt.xlabel('Predicted Label')
    st.pyplot(fig)
    
    # ❗ NEW: HISTORICAL LOG SECTION ❗
    st.write("---")
    st.header("Historical Alert Log")
    if os.path.exists(ALERT_LOG_FILE):
        df_log = pd.read_csv(ALERT_LOG_FILE)
        st.dataframe(df_log)
    else:
        st.info("No alerts have been logged yet. Start the live analysis to generate alerts.")