from auth import require_login
import streamlit as st
import pandas as pd
import joblib
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, roc_curve, auc
import numpy as np
import os
from database_setup import Session, Alert


# --- Simple User Authentication ---
require_login()

# --- Page Configuration ---
st.set_page_config(page_title="Model Performance", layout="wide")
st.title("📊 Model Performance & Alert Log")
st.write("This page shows the performance of the trained Random Forest model and a historical log of all detected alerts.")

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

    # --- ROC Curve and AUC ---
    st.header("ROC Curve & AUC Score")
    # Binarize y_test for ROC (one-vs-rest)
    from sklearn.preprocessing import label_binarize
    y_test_bin = label_binarize(y_test, classes=range(len(class_names)))
    if hasattr(model, "predict_proba"):
        y_score = model.predict_proba(X_test)
        fpr = dict()
        tpr = dict()
        roc_auc = dict()
        for i in range(len(class_names)):
            fpr[i], tpr[i], _ = roc_curve(y_test_bin[:, i], y_score[:, i])
            roc_auc[i] = auc(fpr[i], tpr[i])
        # Plot all ROC curves
        fig_roc, ax_roc = plt.subplots(figsize=(10, 8))
        for i, name in enumerate(class_names):
            ax_roc.plot(fpr[i], tpr[i], label=f"{name} (AUC = {roc_auc[i]:.2f})")
        ax_roc.plot([0, 1], [0, 1], 'k--', lw=2)
        ax_roc.set_xlim([0.0, 1.0])
        ax_roc.set_ylim([0.0, 1.05])
        ax_roc.set_xlabel('False Positive Rate')
        ax_roc.set_ylabel('True Positive Rate')
        ax_roc.set_title('Receiver Operating Characteristic (ROC)')
        ax_roc.legend(loc="lower right")
        st.pyplot(fig_roc)
    else:
        st.info("Model does not support probability prediction for ROC curve.")

    # --- HISTORICAL LOG SECTION - READING FROM DATABASE ---
    st.write("---")
    st.header("Historical Alert Log")
    session = Session()
    try:
        alerts = session.query(Alert).order_by(Alert.timestamp.desc()).limit(1000).all() # Get last 1000 alerts
        if alerts:
            df_log = pd.DataFrame([alert.__dict__ for alert in alerts])
            if '_sa_instance_state' in df_log.columns:
                df_log = df_log.drop(columns=['_sa_instance_state'])

            # --- Filtering UI ---
            st.subheader("Filter Alerts")
            attack_types = df_log['known_attack_type'].unique().tolist()
            selected_attack = st.selectbox("Attack Type", ["All"] + attack_types)
            min_date = df_log['timestamp'].min()
            max_date = df_log['timestamp'].max()
            date_range = st.date_input("Date Range", [min_date, max_date])
            filtered = df_log.copy()
            if selected_attack != "All":
                filtered = filtered[filtered['known_attack_type'] == selected_attack]
            if len(date_range) == 2:
                filtered = filtered[(filtered['timestamp'] >= pd.to_datetime(date_range[0])) & (filtered['timestamp'] <= pd.to_datetime(date_range[1]))]

            st.dataframe(filtered)

            # --- Alert Count Plot ---
            st.subheader("Alert Counts by Type")
            alert_counts = filtered['known_attack_type'].value_counts()
            fig_count, ax_count = plt.subplots()
            alert_counts.plot(kind='bar', ax=ax_count)
            ax_count.set_ylabel('Count')
            ax_count.set_title('Alert Counts by Attack Type')
            st.pyplot(fig_count)
        else:
            st.info("No alerts have been logged yet. Start the live analysis to generate alerts.")
    except Exception as e:
        st.error(f"Error retrieving alerts from database: {e}")
    finally:
        session.close()