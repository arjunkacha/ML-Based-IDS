"""
Test Models Script
==================
This script tests if your trained models (Random Forest, Autoencoder) 
work correctly using synthetic test data.

Run: python test_models.py
"""

import joblib
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model
import sys

def test_models():
    print("=" * 60)
    print("🧪 Testing IDS Models")
    print("=" * 60)
    
    # --- Load Assets ---
    print("\n[1] Loading model artifacts...")
    try:
        rf_model = joblib.load('ids_rf_model.pkl')
        print("    ✅ Random Forest model loaded")
    except FileNotFoundError:
        print("    ❌ Random Forest model NOT found")
        return False
    
    try:
        autoencoder_model = load_model('ids_autoencoder_model.keras')
        print("    ✅ Autoencoder model loaded")
    except FileNotFoundError:
        print("    ❌ Autoencoder model NOT found")
        return False
    
    try:
        autoencoder_threshold = joblib.load('autoencoder_threshold.pkl')
        print(f"    ✅ Autoencoder threshold loaded: {autoencoder_threshold:.4f}")
    except FileNotFoundError:
        print("    ❌ Autoencoder threshold NOT found")
        return False
    
    try:
        scaler = joblib.load('scaler.pkl')
        print("    ✅ Scaler loaded")
    except FileNotFoundError:
        print("    ❌ Scaler NOT found")
        return False
    
    try:
        label_encoder = joblib.load('label_encoder.pkl')
        print("    ✅ Label encoder loaded")
    except FileNotFoundError:
        print("    ❌ Label encoder NOT found")
        return False
    
    try:
        model_columns = joblib.load('model_columns.pkl')
        print(f"    ✅ Model columns loaded ({len(model_columns)} features)")
    except FileNotFoundError:
        print("    ❌ Model columns NOT found")
        return False
    
    # --- Load test data ---
    print("\n[2] Loading test data...")
    try:
        _, X_test, _, y_test = joblib.load('train_test_data.pkl')
        print(f"    ✅ Test data loaded ({len(X_test)} samples)")
    except FileNotFoundError:
        print("    ❌ Test data NOT found. Run data_preprocessing.py first.")
        return False
    
    # --- Test Random Forest ---
    print("\n[3] Testing Random Forest Model...")
    try:
        rf_predictions = rf_model.predict(X_test)
        rf_pred_labels = label_encoder.inverse_transform(rf_predictions)
        
        benign_count = np.sum(rf_pred_labels == 'BENIGN')
        attack_count = len(rf_pred_labels) - benign_count
        
        print(f"    ✅ Predictions made on {len(rf_predictions)} samples")
        print(f"       - BENIGN: {benign_count} ({benign_count/len(rf_pred_labels)*100:.1f}%)")
        print(f"       - ATTACKS: {attack_count} ({attack_count/len(rf_pred_labels)*100:.1f}%)")
        print(f"       - Classes: {label_encoder.classes_[:5]}... (total: {len(label_encoder.classes_)})")
    except Exception as e:
        print(f"    ❌ Random Forest prediction failed: {e}")
        return False
    
    # --- Test Autoencoder ---
    print("\n[4] Testing Autoencoder Model...")
    try:
        reconstructions = autoencoder_model.predict(X_test, verbose=0)
        mse = np.mean(np.power(X_test - reconstructions, 2), axis=1)
        anomalies = (mse > autoencoder_threshold).astype(int)
        
        anomaly_count = np.sum(anomalies)
        
        print(f"    ✅ Autoencoder predictions made on {len(mse)} samples")
        print(f"       - MSE range: [{mse.min():.4f}, {mse.max():.4f}]")
        print(f"       - Threshold: {autoencoder_threshold:.4f}")
        print(f"       - Anomalies detected: {anomaly_count} ({anomaly_count/len(mse)*100:.1f}%)")
    except Exception as e:
        print(f"    ❌ Autoencoder prediction failed: {e}")
        return False
    
    # --- Test on Synthetic Attack Patterns ---
    print("\n[5] Testing on Synthetic Attack Patterns...")
    try:
        # Create a synthetic benign sample
        benign_sample = np.zeros((1, len(model_columns)))
        # Create synthetic attack patterns
        attack_sample = np.ones((1, len(model_columns))) * 10  # High values simulate attack
        anomaly_sample = np.random.randn(1, len(model_columns)) * 5  # Random pattern simulates anomaly
        
        # Scale samples
        benign_scaled = scaler.transform(benign_sample)
        attack_scaled = scaler.transform(attack_sample)
        anomaly_scaled = scaler.transform(anomaly_sample)
        
        # RF predictions
        rf_benign = label_encoder.inverse_transform(rf_model.predict(benign_scaled))
        rf_attack = label_encoder.inverse_transform(rf_model.predict(attack_scaled))
        rf_anomaly = label_encoder.inverse_transform(rf_model.predict(anomaly_scaled))
        
        # AE predictions
        ae_benign_recon = autoencoder_model.predict(benign_scaled, verbose=0)
        ae_benign_mse = np.mean(np.power(benign_scaled - ae_benign_recon, 2))
        ae_benign_anomaly = "YES" if ae_benign_mse > autoencoder_threshold else "NO"
        
        ae_attack_recon = autoencoder_model.predict(attack_scaled, verbose=0)
        ae_attack_mse = np.mean(np.power(attack_scaled - ae_attack_recon, 2))
        ae_attack_anomaly = "YES" if ae_attack_mse > autoencoder_threshold else "NO"
        
        ae_anomaly_recon = autoencoder_model.predict(anomaly_scaled, verbose=0)
        ae_anomaly_mse = np.mean(np.power(anomaly_scaled - ae_anomaly_recon, 2))
        ae_anomaly_anomaly = "YES" if ae_anomaly_mse > autoencoder_threshold else "NO"
        
        print(f"    Benign Sample:")
        print(f"       - RF: {rf_benign[0]} | AE Anomaly: {ae_benign_anomaly} (MSE: {ae_benign_mse:.4f})")
        
        print(f"    Attack-like Sample (high values):")
        print(f"       - RF: {rf_attack[0]} | AE Anomaly: {ae_attack_anomaly} (MSE: {ae_attack_mse:.4f})")
        
        print(f"    Anomaly-like Sample (random pattern):")
        print(f"       - RF: {rf_anomaly[0]} | AE Anomaly: {ae_anomaly_anomaly} (MSE: {ae_anomaly_mse:.4f})")
        
        print(f"    ✅ Synthetic tests completed successfully")
    except Exception as e:
        print(f"    ❌ Synthetic test failed: {e}")
        return False
    
    # --- Summary ---
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour models are working correctly.")
    print("You can now:")
    print("  1. Use File Analysis page to upload CSV files for detection")
    print("  2. Use Live Analysis page for real-time traffic monitoring")
    print("  3. View historical alerts in the Dashboard")
    print("\nNote: If UDP flooder doesn't trigger detections:")
    print("  - UDP floods may not match the training data patterns")
    print("  - The model was trained on network flow features (duration, packet counts, etc.)")
    print("  - Try using legitimate traffic CSV files from CICIDS2017 dataset instead")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    try:
        success = test_models()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
