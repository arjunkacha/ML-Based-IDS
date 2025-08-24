import joblib
import pandas as pd
import numpy as np
from scapy.all import sniff

# --- 1. Load Pre-trained Assets ---
print("🔹 Loading saved model and preprocessors...")
try:
    model = joblib.load('ids_rf_model.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
    model_columns = joblib.load('model_columns.pkl')
    print("✅ Assets loaded successfully.")
except FileNotFoundError:
    print("❌ Error: Required model assets not found. Make sure all .pkl files are present.")
    exit()

# --- 2. Define the Packet Processing Function ---
def process_packet(packet):
    """
    Processes a single packet and predicts if it's an intrusion.
    """
    try:
        # --- Feature Extraction (Simplified for real-time) ---
        # This is a simplified mapping from packet data to the model's expected features.
        # NOTE: Many features from the original dataset are flow-based (aggregates over time).
        # We are approximating them on a per-packet basis here.
        
        feature_dict = {col: 0 for col in model_columns} # Initialize all features to 0

        if packet.haslayer('IP'):
            feature_dict['Source Port'] = packet.sport
            feature_dict['Destination Port'] = packet.dport
        
        if packet.haslayer('TCP'):
            feature_dict['Protocol'] = 6 # TCP protocol number
            feature_dict['Total Length of Fwd Packets'] = len(packet[TCP].payload)
            feature_dict['Fwd Packet Length Max'] = len(packet[TCP].payload)
            feature_dict['Fwd Packet Length Mean'] = len(packet[TCP].payload)
        elif packet.haslayer('UDP'):
            feature_dict['Protocol'] = 17 # UDP protocol number
            feature_dict['Total Length of Fwd Packets'] = len(packet[UDP].payload)
            feature_dict['Fwd Packet Length Max'] = len(packet[UDP].payload)
            feature_dict['Fwd Packet Length Mean'] = len(packet[UDP].payload)
            
        # Create a DataFrame from the extracted features
        df_packet = pd.DataFrame([feature_dict], columns=model_columns)
        
        # --- Preprocessing and Prediction ---
        # Scale the features using the loaded scaler
        packet_scaled = scaler.transform(df_packet)
        
        # Make a prediction
        prediction = model.predict(packet_scaled)
        attack_label = label_encoder.inverse_transform(prediction)[0]
        
        # --- Alerting ---
        if attack_label != 'BENIGN':
            print(f"🚨 ALERT! Potential Intrusion Detected: {attack_label.upper()} | Source IP: {packet['IP'].src} | Dest IP: {packet['IP'].dst}")

    except (AttributeError, IndexError):
        # Ignore packets that don't have the expected layers (e.g., ARP)
        pass

# --- 3. Start Sniffing ---
print("\n🚀 Starting live network traffic analysis... (Press Ctrl+C to stop)")
# 'prn' calls the process_packet function for every packet captured.
# 'store=0' tells Scapy not to store packets in memory.
sniff(prn=process_packet, store=0)