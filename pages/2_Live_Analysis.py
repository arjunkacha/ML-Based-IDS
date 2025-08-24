import streamlit as st
import pandas as pd
import joblib
import numpy as np
from scapy.all import sniff, IP, TCP, UDP
import time
import os
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(page_title="Hybrid IDS Dashboard", layout="wide")
st.title("🛡️ Hybrid Intrusion Detection Dashboard")
st.write("This dashboard uses two models: a Random Forest for known attacks and an Isolation Forest for unknown anomalies.")

# --- Define Log File ---
ALERT_LOG_FILE = "alert_log.csv"

# --- Load Assets ---
@st.cache_resource
def load_assets():
    try:
        rf_model = joblib.load('ids_rf_model.pkl')
        iforest_model = joblib.load('ids_iforest_model.pkl')
        scaler = joblib.load('scaler.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
        model_columns = joblib.load('model_columns.pkl')
        return rf_model, iforest_model, scaler, label_encoder, model_columns
    except FileNotFoundError as e:
        st.error(f"Error loading assets: {e}. Please ensure all .pkl files are present.")
        return None, None, None, None, None

rf_model, iforest_model, scaler, label_encoder, model_columns = load_assets()

# --- Initialize Session State ---
if 'sniffing' not in st.session_state:
    st.session_state.sniffing = False
if 'captured_packets' not in st.session_state:
    st.session_state.captured_packets = []

# --- Packet Processing Function ---
def process_packet(packet):
    feature_dict = {col: 0 for col in model_columns}
    if packet.haslayer('IP'):
        feature_dict['Source Port'] = packet.sport
        feature_dict['Destination Port'] = packet.dport
    if packet.haslayer('TCP'):
        feature_dict['Protocol'] = 6
    elif packet.haslayer('UDP'):
        feature_dict['Protocol'] = 17
    st.session_state.captured_packets.append(feature_dict)

# --- UI Controls ---
col1, col2 = st.columns(2)
if col1.button('Start Sniffing', type="primary"):
    st.session_state.sniffing = True
    st.session_state.captured_packets = []
if col2.button('Stop Sniffing'):
    st.session_state.sniffing = False

# --- Live Sniffing and Display Logic ---
if st.session_state.sniffing and all([rf_model, iforest_model, scaler]):
    st.info("Sniffing live traffic... Capturing 15 packets per cycle.")
    sniff(prn=process_packet, store=0, count=15, timeout=5)
    
    if st.session_state.captured_packets:
        df_captured = pd.DataFrame(st.session_state.captured_packets)
        df_processed = df_captured.reindex(columns=model_columns, fill_value=0)
        X_scaled = scaler.transform(df_processed)
        
        rf_predictions_num = rf_model.predict(X_scaled)
        rf_predictions = label_encoder.inverse_transform(rf_predictions_num)
        iforest_predictions = iforest_model.predict(X_scaled)
        
        df_captured['Known Attack Type'] = rf_predictions
        df_captured['Anomaly Detected'] = np.where(iforest_predictions == -1, 'Yes', 'No')
        
        df_attacks = df_captured[
            (df_captured['Known Attack Type'] != 'BENIGN') | 
            (df_captured['Anomaly Detected'] == 'Yes')
        ].copy()

        st.write("---")
        st.header("Detected Intrusions & Anomalies")
        if not df_attacks.empty:
            st.dataframe(df_attacks)
            # ❗ NEW: LOGGING LOGIC ❗
            df_attacks['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Check if log file exists to decide on writing header
            header = not os.path.exists(ALERT_LOG_FILE)
            df_attacks.to_csv(ALERT_LOG_FILE, mode='a', header=header, index=False)
        else:
            st.success("✅ No intrusions or anomalies detected in the last capture.")
    
    time.sleep(1)
    st.rerun()
else:
    st.info("Press 'Start Sniffing' to begin live network analysis.")