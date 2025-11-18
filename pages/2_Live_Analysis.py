import streamlit as st
from auth import require_login
import pandas as pd
import joblib
import numpy as np
from scapy.all import sniff, IP, TCP, UDP
import time
import threading
from tensorflow.keras.models import load_model
from queue import Queue
from database_setup import Session, Alert
from datetime import datetime

st.set_page_config(page_title="Advanced Live IDS", layout="wide")
require_login()
st.title("🛡️ Advanced Live IDS")
st.write("Real-time network intrusion detection using packet capture.")

# --- Global state ---
packet_queue = Queue()
results_queue = Queue()

# --- Load Assets ---
@st.cache_resource
def load_assets():
    try:
        rf_model = joblib.load('ids_rf_model.pkl')
        autoencoder_model = load_model('ids_autoencoder_model.keras') 
        autoencoder_threshold = joblib.load('autoencoder_threshold.pkl')
        scaler = joblib.load('scaler.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
        model_columns = joblib.load('model_columns.pkl')
        return rf_model, autoencoder_model, autoencoder_threshold, scaler, label_encoder, model_columns
    except FileNotFoundError as e:
        st.error(f"❌ Error loading assets: {e}")
        return None, None, None, None, None, None

rf_model, autoencoder_model, autoencoder_threshold, scaler, label_encoder, model_columns = load_assets()

# --- Initialize Session State ---
if 'sniffing' not in st.session_state:
    st.session_state.sniffing = False
if 'detected_alerts' not in st.session_state:
    st.session_state.detected_alerts = []

# --- Packet Processing ---
def get_flow_key(packet):
    """Extract 5-tuple from packet."""
    try:
        if IP in packet:
            if TCP in packet:
                return (packet[IP].src, packet[TCP].sport, packet[IP].dst, packet[TCP].dport, 6)
            elif UDP in packet:
                return (packet[IP].src, packet[UDP].sport, packet[IP].dst, packet[UDP].dport, 17)
    except:
        pass
    return None

def process_packet(packet):
    """Capture packet and put in queue."""
    flow_key = get_flow_key(packet)
    if flow_key:
        packet_queue.put((flow_key, len(packet)))

# --- Analysis Thread ---
def analyze_packets():
    """Continuously analyze buffered packets."""
    packet_buffer = []
    
    while st.session_state.get('sniffing', False):
        time.sleep(2)  # Analyze every 2 seconds
        
        # Collect buffered packets
        while not packet_queue.empty() and len(packet_buffer) < 100:
            try:
                packet_buffer.append(packet_queue.get_nowait())
            except:
                break
        
        if not packet_buffer:
            continue
        
        # Process batch
        try:
            flows_to_predict = []
            for flow_key, pkt_len in packet_buffer:
                features = {col: 0 for col in model_columns}
                features['Flow Duration'] = 100000
                features['Tot Fwd Pkts'] = 1
                features['TotLen Fwd Pkts'] = pkt_len
                features['Fwd Pkt Len Max'] = pkt_len
                features['Fwd Pkt Len Min'] = pkt_len
                features['Fwd Pkt Len Mean'] = pkt_len
                features['Fwd Pkt Len Std'] = 0
                features['Fwd Pkts/s'] = 1
                features['Fwd IAT Mean'] = 0
                features['Fwd IAT Std'] = 0
                features['Fwd IAT Max'] = 0
                features['Fwd IAT Min'] = 0
                
                flows_to_predict.append((flow_key, features))
            
            # Convert to DataFrame
            df_predict = pd.DataFrame([f for _, f in flows_to_predict]).reindex(columns=model_columns, fill_value=0)
            X_scaled = scaler.transform(df_predict)
            
            # Predictions
            rf_preds = label_encoder.inverse_transform(rf_model.predict(X_scaled))
            reconstructions = autoencoder_model.predict(X_scaled, verbose=0)
            mse = np.mean(np.power(X_scaled - reconstructions, 2), axis=1)
            ae_preds = (mse > autoencoder_threshold)
            
            # Find attacks
            for idx, (flow_key, _) in enumerate(flows_to_predict):
                is_attack = (rf_preds[idx] != 'BENIGN') or ae_preds[idx]
                
                if is_attack:
                    src_ip, src_port, dst_ip, dst_port, proto = flow_key
                    alert = {
                        'timestamp': datetime.now(),
                        'Source IP': src_ip,
                        'Source Port': src_port,
                        'Destination IP': dst_ip,
                        'Destination Port': dst_port,
                        'Protocol': proto,
                        'Attack Type': str(rf_preds[idx]),
                        'Anomaly MSE': float(mse[idx]),
                        'Threshold': float(autoencoder_threshold)
                    }
                    
                    # Log to database
                    session = Session()
                    try:
                        db_alert = Alert(
                            timestamp=alert['timestamp'],
                            source_port=alert['Source Port'],
                            destination_port=alert['Destination Port'],
                            protocol=alert['Protocol'],
                            total_length_fwd_packets=0,
                            known_attack_type=alert['Attack Type'],
                            anomaly_detected=ae_preds[idx]
                        )
                        session.add(db_alert)
                        session.commit()
                    except Exception as e:
                        session.rollback()
                    finally:
                        session.close()
                    
                    results_queue.put(alert)
            
            packet_buffer.clear()
            
        except Exception as e:
            st.error(f"Analysis error: {e}")
            packet_buffer.clear()

# --- UI Controls ---
col1, col2 = st.columns(2)

if col1.button('🔴 Start Capture', type="primary", key="start"):
    if not st.session_state.sniffing:
        st.session_state.sniffing = True
        st.session_state.detected_alerts = []
        
        # Start analyzer thread
        analyzer = threading.Thread(target=analyze_packets, daemon=True)
        analyzer.start()
        
        # Start sniffer thread
        def sniff_packets():
            sniff(prn=process_packet, store=0, iface=None, 
                  stop_filter=lambda p: not st.session_state.sniffing)
        
        sniffer = threading.Thread(target=sniff_packets, daemon=True)
        sniffer.start()
        
        st.rerun()

if col2.button('⏹️ Stop Capture', key="stop"):
    st.session_state.sniffing = False
    st.rerun()

if st.session_state.sniffing:
    st.success("🟢 **CAPTURING** - Run nmap now: `nmap -sS -p 1-1000 localhost`")
    
    # Poll for results
    while not results_queue.empty():
        try:
            alert = results_queue.get_nowait()
            st.session_state.detected_alerts.append(alert)
        except:
            break
    
    # Display detected attacks
    if st.session_state.detected_alerts:
        st.write("---")
        st.header("🚨 Detected Attacks")
        df_alerts = pd.DataFrame(st.session_state.detected_alerts)
        st.dataframe(df_alerts, use_container_width=True)
    else:
        st.info("⏳ Waiting for attacks... (Scanning now?)")
    
    time.sleep(2)
    st.rerun()
else:
    st.info("Click **Start Capture** to begin monitoring")

# --- Historical Alert Log ---
st.write("---")
st.header("📊 Historical Alert Log")

session = Session()
try:
    alerts = session.query(Alert).order_by(Alert.timestamp.desc()).limit(500).all()
    if alerts:
        df_log = pd.DataFrame([{
            'Timestamp': a.timestamp,
            'Source Port': a.source_port,
            'Destination Port': a.destination_port,
            'Protocol': a.protocol,
            'Attack Type': a.known_attack_type,
            'Is Anomaly': a.anomaly_detected
        } for a in alerts])
        
        # Filters
        col_filter1, col_filter2 = st.columns(2)
        attack_types = df_log['Attack Type'].unique().tolist()
        selected_attack = col_filter1.multiselect('Filter by Attack Type', attack_types, default=attack_types)
        df_filtered = df_log[df_log['Attack Type'].isin(selected_attack)]
        
        st.dataframe(df_filtered, use_container_width=True)
        st.write(f"**Total alerts: {len(df_filtered)}**")
    else:
        st.info("No alerts in database yet.")
except Exception as e:
    st.error(f"Error loading alerts: {e}")
finally:
    session.close()
