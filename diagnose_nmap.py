"""
Diagnostic script to test nmap detection in real-time.
Shows raw packets captured and whether they're being detected as attacks.
"""

import joblib
import numpy as np
from scapy.all import sniff, IP, TCP, UDP
from tensorflow.keras.models import load_model
import time

print("=" * 70)
print("NMAP DETECTION DIAGNOSTIC TOOL")
print("=" * 70)

# Load models
try:
    print("\n[1] Loading models...")
    rf_model = joblib.load('ids_rf_model.pkl')
    autoencoder_model = load_model('ids_autoencoder_model.keras')
    autoencoder_threshold = joblib.load('autoencoder_threshold.pkl')
    scaler = joblib.load('scaler.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
    model_columns = joblib.load('model_columns.pkl')
    print("    ✅ All models loaded successfully")
except Exception as e:
    print(f"    ❌ Error loading models: {e}")
    exit(1)

packet_count = 0
attack_count = 0

def analyze_packet(packet):
    global packet_count, attack_count
    
    # Capture packet info
    src_ip = "N/A"
    dst_ip = "N/A"
    src_port = 0
    dst_port = 0
    proto = "?"
    
    if IP in packet:
        src_ip = packet[IP].src
        dst_ip = packet[IP].dst
        
        if TCP in packet:
            src_port = packet[TCP].sport
            dst_port = packet[TCP].dport
            proto = "TCP"
        elif UDP in packet:
            src_port = packet[UDP].sport
            dst_port = packet[UDP].dport
            proto = "UDP"
    
    packet_count += 1
    
    # Extract features (same as Live Analysis)
    features = {col: 0 for col in model_columns}
    features['Flow Duration'] = 1000000
    features['Tot Fwd Pkts'] = 1
    features['TotLen Fwd Pkts'] = len(packet)
    features['Fwd Pkt Len Max'] = len(packet)
    features['Fwd Pkt Len Min'] = len(packet)
    features['Fwd Pkt Len Mean'] = len(packet)
    
    df = np.array([[features[col] for col in model_columns]])
    X_scaled = scaler.transform(df)
    
    # Predict
    rf_pred = label_encoder.inverse_transform(rf_model.predict(X_scaled))[0]
    
    rec = autoencoder_model.predict(X_scaled, verbose=0)
    mse = np.mean(np.power(X_scaled - rec, 2))
    is_anomaly = mse > autoencoder_threshold
    
    # Check if attack
    is_attack = (rf_pred != 'BENIGN') or is_anomaly
    
    if is_attack:
        attack_count += 1
        print(f"\n🚨 [{attack_count}] ATTACK DETECTED!")
        print(f"    {src_ip}:{src_port} → {dst_ip}:{dst_port} ({proto})")
        print(f"    RF Prediction: {rf_pred} | Anomaly MSE: {mse:.4f} | Threshold: {autoencoder_threshold:.4f}")
        print(f"    Packet size: {len(packet)} bytes")

print("\n[2] Starting packet sniffer...")
print("    💡 Run this in another terminal: nmap -sS -p 1-1000 localhost")
print("    Or use Zenmap: Target=localhost, Profile='Intense Scan'")
print("\n    Listening for packets for 60 seconds...\n")

try:
    sniff(prn=analyze_packet, store=0, timeout=60)
except KeyboardInterrupt:
    print("\n\n[!] Interrupted by user")

print("\n" + "=" * 70)
print(f"CAPTURE COMPLETE")
print("=" * 70)
print(f"Total packets captured: {packet_count}")
print(f"Attacks detected: {attack_count}")
if packet_count == 0:
    print("\n⚠️  WARNING: No packets captured!")
    print("   - Firewall may be blocking")
    print("   - Nmap may be scanning without generating packets on this interface")
    print("   - Try running as Administrator")
elif attack_count == 0:
    print("\n⚠️  WARNING: Packets captured but no attacks detected!")
    print("   - Models may need retraining on nmap patterns")
    print("   - Try File Analysis with synthetic_portscan.csv instead")
else:
    print(f"\n✅ SUCCESS! Detected {attack_count}/{packet_count} packets as attacks ({100*attack_count//packet_count}%)")
print("=" * 70)
