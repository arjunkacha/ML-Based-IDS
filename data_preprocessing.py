import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import numpy as np

# --- 1. Load and Combine Data ---
DATA_DIR = "MachineLearningCSV/MachineLearningCVE"


def load_data(data_dir):
    """Loads all CSV files from a directory into a single DataFrame."""
    combined_df = pd.DataFrame()
    for file in os.listdir(data_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(data_dir, file)
            print(f"🔹 Loading: {file}")
            df = pd.read_csv(file_path, low_memory=False)
            combined_df = pd.concat([combined_df, df], ignore_index=True)
    return combined_df


# --- 2. Preprocess the Dataset ---
def preprocess_data(df):
    """Cleans, encodes, and scales the dataset."""
    print("\n🔹 Starting preprocessing...")
    print("Initial shape:", df.shape)

    df.columns = df.columns.str.strip()

    if 'Flow ID' in df.columns and 'Timestamp' in df.columns:
        df.drop(columns=['Flow ID', 'Timestamp'], inplace=True)

    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)

    print("Shape after dropping nulls/infinities:", df.shape)

    label_encoder = LabelEncoder()
    df['Label'] = label_encoder.fit_transform(df['Label'])
    joblib.dump(label_encoder, 'label_encoder.pkl')
    print("LabelEncoder saved to 'label_encoder.pkl'")

    X = df.drop('Label', axis=1)
    y = df['Label']

    # This is the line you were adding
    joblib.dump(X.columns, 'model_columns.pkl')
    print("Model columns saved to 'model_columns.pkl'")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    joblib.dump(scaler, 'scaler.pkl')
    print("StandardScaler saved to 'scaler.pkl'")

    return X_scaled, y


# --- 3. Main execution block ---
if __name__ == "__main__":
    full_df = load_data(DATA_DIR)

    X_processed, y_processed = preprocess_data(full_df)

    print("\n🔹 Splitting data into training and testing sets (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=0.2, random_state=42,
                                                        stratify=y_processed)

    joblib.dump((X_train, X_test, y_train, y_test), 'train_test_data.pkl')

    print("\n✅ Preprocessing complete!")
    print("Processed and split data saved to 'train_test_data.pkl'")