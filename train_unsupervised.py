import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest

print("🔹 Loading preprocessed data...")
try:
    X_train, _, y_train, _ = joblib.load('train_test_data.pkl')
    label_encoder = joblib.load('label_encoder.pkl')
except FileNotFoundError:
    print("❌ Error: Required .pkl files not found. Please run data_preprocessing.py first.")
    exit()

# We need to find which numerical label corresponds to 'BENIGN'
benign_label_numeric = label_encoder.transform(['BENIGN'])[0]

# Filter the training data to get ONLY the BENIGN traffic
X_train_benign = X_train[y_train == benign_label_numeric]

print(f"✅ Data loaded. Training Isolation Forest on {len(X_train_benign)} BENIGN samples...")

# --- Train the Isolation Forest Model ---
# contamination='auto' is a good starting point. It means the model will try to
# estimate the proportion of outliers in the data.
iforest_model = IsolationForest(n_estimators=100, contamination='auto', random_state=42, n_jobs=-1)
iforest_model.fit(X_train_benign)

print("✅ Training complete.")

# --- Save the Trained Model ---
joblib.dump(iforest_model, 'ids_iforest_model.pkl')
print("💾 Unsupervised model saved to 'ids_iforest_model.pkl'")