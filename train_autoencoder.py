import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.callbacks import EarlyStopping
import seaborn as sns
import matplotlib.pyplot as plt


def train_and_evaluate_autoencoder():
    """
    Trains, evaluates, and saves an Autoencoder model for anomaly detection.
    """
    print("--- Training Autoencoder Model ---")

    # Load preprocessed data
    print("🔹 Loading preprocessed data from 'train_test_data.pkl'...")
    try:
        X_train_full, X_test_full, y_train_full, y_test_full = joblib.load('train_test_data.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
    except FileNotFoundError:
        print("Error: Required .pkl files not found. Please run data_preprocessing.py first.")
        exit()

    # Get 'BENIGN' label index
    benign_label_idx = np.where(label_encoder.classes_ == 'BENIGN')[0][0]

    # Filter for BENIGN data only for training the autoencoder
    X_train_benign = X_train_full[y_train_full == benign_label_idx]
    X_test_benign = X_test_full[y_test_full == benign_label_idx]

    print(f"Number of BENIGN samples for Autoencoder training: {len(X_train_benign)}")
    print(f"Number of BENIGN samples for Autoencoder testing: {len(X_test_benign)}")

    # --- Build the Autoencoder Model ---
    input_dim = X_train_benign.shape[1]
    encoding_dim = int(input_dim / 2)  # Example: Half the input dimensions
    latent_dim = int(encoding_dim / 2)  # Even smaller bottleneck

    input_layer = Input(shape=(input_dim,))

    # Encoder
    encoder = Dense(encoding_dim, activation="relu")(input_layer)
    encoder = Dense(latent_dim, activation="relu")(encoder)

    # Decoder
    decoder = Dense(encoding_dim, activation="relu")(encoder)
    decoder = Dense(input_dim, activation="linear")(decoder)  # Linear for standardized data

    autoencoder = Model(inputs=input_layer, outputs=decoder)
    autoencoder.compile(optimizer='adam', loss='mse')  # Mean Squared Error is common for autoencoders

    print("\nAutoencoder Model Summary:")
    autoencoder.summary()

    # --- Train the Autoencoder ---
    # Use early stopping to prevent overfitting
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    history = autoencoder.fit(X_train_benign, X_train_benign,
                              epochs=50,
                              batch_size=32,
                              shuffle=True,
                              validation_data=(X_test_benign, X_test_benign),
                              callbacks=[early_stopping],
                              verbose=1)

    print("\n✅ Autoencoder training complete!")

    # --- Evaluate Anomaly Threshold ---
    # Get reconstruction errors for benign data
    benign_reconstructions = autoencoder.predict(X_train_benign)
    benign_loss = np.mean(np.power(X_train_benign - benign_reconstructions, 2), axis=1)

    # Set a threshold (e.g., mean + X * standard deviation of benign loss)
    threshold = np.mean(benign_loss) + 2 * np.std(benign_loss)  # Common heuristic
    print(f"Calculated Anomaly Threshold: {threshold:.4f}")

    # Save the trained autoencoder model and the threshold
    autoencoder.save('ids_autoencoder_model.keras')  # Keras models use .h5 or .keras
    joblib.dump(threshold, 'autoencoder_threshold.pkl')
    print("\n💾 Autoencoder model saved to 'ids_autoencoder_model.keras'")
    print("💾 Anomaly threshold saved to 'autoencoder_threshold.pkl'")

    # --- Visualization of Loss Distribution ---
    plt.figure(figsize=(10, 6))
    sns.histplot(benign_loss, bins=50, kde=True, color='blue', label='Benign Loss')
    plt.axvline(threshold, color='red', linestyle='--', label=f'Threshold: {threshold:.4f}')
    plt.title('Reconstruction Loss Distribution for Benign Traffic')
    plt.xlabel('Reconstruction Loss (MSE)')
    plt.ylabel('Number of Samples')
    plt.legend()
    plt.show()


# --- Main execution block ---
if __name__ == "__main__":
    train_and_evaluate_autoencoder()
    print("\n✅ Autoencoder training and evaluation complete!")