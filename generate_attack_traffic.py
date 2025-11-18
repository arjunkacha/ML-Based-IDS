"""
Synthetic Attack Traffic Generator
===================================
Generates synthetic network traffic CSV files with known attack patterns.
Use these with File Analysis page to test your models.

Run: python generate_attack_traffic.py
Output: synthetic_benign.csv, synthetic_ddos.csv, synthetic_portscan.csv
"""

import pandas as pd
import numpy as np
import joblib

def generate_synthetic_traffic():
    """Generate synthetic traffic samples with attack patterns."""
    
    # Load model columns to know what features to generate
    try:
        model_columns = joblib.load('model_columns.pkl')
    except FileNotFoundError:
        print("❌ model_columns.pkl not found. Run data_preprocessing.py first.")
        return False
    
    print(f"Generating synthetic traffic with {len(model_columns)} features...")
    
    # --- BENIGN TRAFFIC ---
    print("\n[1] Generating BENIGN traffic...")
    benign_samples = []
    for i in range(100):
        # Build sample as dict keyed by column name to ensure correct mapping
        sample = {col: float(np.random.randn() * 0.5) for col in model_columns}
        # Keep values moderate for benign traffic
        for k in sample:
            sample[k] = float(np.clip(sample[k], -2, 2))
        benign_samples.append(sample)
    
    df_benign = pd.DataFrame(benign_samples, columns=model_columns)
    df_benign['Label'] = 'BENIGN'
    df_benign.to_csv('synthetic_benign.csv', index=False)
    print(f"    ✅ Generated 100 benign samples → synthetic_benign.csv")
    
    # --- DDoS ATTACK TRAFFIC ---
    print("\n[2] Generating DDoS attack traffic...")
    ddos_samples = []
    for i in range(50):
        # Start from a noisy baseline then set attack-specific fields by name
        sample = {col: float(np.random.randn() * 2) for col in model_columns}
        # DDoS characteristics: high flow duration, high forward packet counts, high forward bytes
        if 'Flow Duration' in sample:
            sample['Flow Duration'] = float(np.random.uniform(10000, 100000))
        if 'Total Fwd Packets' in sample:
            sample['Total Fwd Packets'] = float(np.random.uniform(500, 5000))
        if 'Total Length of Fwd Packets' in sample:
            sample['Total Length of Fwd Packets'] = float(np.random.uniform(100000, 1000000))
        # Also set other high-importance features to attackish values
        if 'Destination Port' in sample:
            sample['Destination Port'] = float(np.random.choice([80, 443, 8080]))
        if 'Init_Win_bytes_backward' in sample:
            sample['Init_Win_bytes_backward'] = float(np.random.uniform(10000, 200000))
        if 'Max Packet Length' in sample:
            sample['Max Packet Length'] = float(np.random.uniform(1200, 65535))
        if 'Subflow Fwd Bytes' in sample:
            sample['Subflow Fwd Bytes'] = float(np.random.uniform(10000, 500000))
        # Clip to reasonable numeric bounds
        for k in sample:
            sample[k] = float(np.clip(sample[k], -1e6, 1e7))
        ddos_samples.append(sample)
    
    df_ddos = pd.DataFrame(ddos_samples, columns=model_columns)
    df_ddos['Label'] = 'DDoS'
    df_ddos.to_csv('synthetic_ddos.csv', index=False)
    print(f"    ✅ Generated 50 DDoS samples → synthetic_ddos.csv")
    
    # --- PORT SCAN TRAFFIC ---
    print("\n[3] Generating Port Scan attack traffic...")
    portscan_samples = []
    for i in range(50):
        sample = {col: float(np.random.randn() * 1.5) for col in model_columns}
        # Port scan characteristics: moderate packet counts, low-to-moderate bytes
        if 'Total Fwd Packets' in sample:
            sample['Total Fwd Packets'] = float(np.random.uniform(100, 500))
        if 'Total Length of Fwd Packets' in sample:
            sample['Total Length of Fwd Packets'] = float(np.random.uniform(5000, 50000))
        for k in sample:
            sample[k] = float(np.clip(sample[k], -1e5, 1e6))
        portscan_samples.append(sample)
    
    df_portscan = pd.DataFrame(portscan_samples, columns=model_columns)
    df_portscan['Label'] = 'PortScan'
    df_portscan.to_csv('synthetic_portscan.csv', index=False)
    print(f"    ✅ Generated 50 Port Scan samples → synthetic_portscan.csv")
    
    # --- MIXED ATTACK TRAFFIC (for realistic testing) ---
    print("\n[4] Generating mixed attack traffic...")
    mixed_samples = []
    mixed_labels = []
    
    for i in range(200):
        attack_type = np.random.choice(['BENIGN', 'DDoS', 'PortScan', 'Infiltration'], p=[0.5, 0.2, 0.15, 0.15])
        
        if attack_type == 'BENIGN':
            sample = {col: float(np.random.randn() * 0.5) for col in model_columns}
            for k in sample:
                sample[k] = float(np.clip(sample[k], -2, 2))
        elif attack_type == 'DDoS':
            sample = {col: float(np.random.randn() * 2) for col in model_columns}
            if 'Flow Duration' in sample:
                sample['Flow Duration'] = float(np.random.uniform(10000, 100000))
            if 'Total Fwd Packets' in sample:
                sample['Total Fwd Packets'] = float(np.random.uniform(500, 5000))
            if 'Total Length of Fwd Packets' in sample:
                sample['Total Length of Fwd Packets'] = float(np.random.uniform(100000, 1000000))
            for k in sample:
                sample[k] = float(np.clip(sample[k], -1e6, 1e7))
        elif attack_type == 'PortScan':
            sample = {col: float(np.random.randn() * 1.5) for col in model_columns}
            if 'Total Fwd Packets' in sample:
                sample['Total Fwd Packets'] = float(np.random.uniform(100, 500))
            if 'Total Length of Fwd Packets' in sample:
                sample['Total Length of Fwd Packets'] = float(np.random.uniform(5000, 50000))
            for k in sample:
                sample[k] = float(np.clip(sample[k], -1e5, 1e6))
        else:  # Infiltration
            sample = {col: float(np.random.randn() * 1.8) for col in model_columns}
            if 'Flow Duration' in sample:
                sample['Flow Duration'] = float(np.random.uniform(50000, 200000))
            if 'Total Fwd Packets' in sample:
                sample['Total Fwd Packets'] = float(np.random.uniform(200, 1000))
            for k in sample:
                sample[k] = float(np.clip(sample[k], -1e6, 1e7))
        
        mixed_samples.append(sample)
        mixed_labels.append(attack_type)
    
    df_mixed = pd.DataFrame(mixed_samples, columns=model_columns)
    df_mixed['Label'] = mixed_labels
    df_mixed.to_csv('synthetic_mixed_traffic.csv', index=False)
    print(f"    ✅ Generated 200 mixed samples → synthetic_mixed_traffic.csv")
    
    print("\n" + "=" * 60)
    print("✅ Synthetic traffic generation complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print("  1. synthetic_benign.csv (100 benign samples)")
    print("  2. synthetic_ddos.csv (50 DDoS samples)")
    print("  3. synthetic_portscan.csv (50 Port Scan samples)")
    print("  4. synthetic_mixed_traffic.csv (200 mixed samples)")
    print("\nUsage:")
    print("  1. Go to File Analysis page in Streamlit")
    print("  2. Upload any of these CSV files")
    print("  3. Models will make predictions")
    print("  4. Alerts will be logged to the database")
    print("\nYou can also manually inspect results:")
    print("  python - <<'PY'")
    print("  import pandas as pd")
    print("  df = pd.read_csv('synthetic_ddos.csv')")
    print("  print(df.head())")
    print("  PY")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    import sys
    try:
        success = generate_synthetic_traffic()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
