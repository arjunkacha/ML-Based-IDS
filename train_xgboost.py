import joblib
import xgboost as xgb
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd


def train_and_evaluate_xgboost(X_train, y_train, X_test, y_test, class_names):
    """
    Trains, evaluates, and saves an XGBoost model.
    """
    print("--- Training XGBoost Model ---")

    # Initialize the XGBoost Classifier
    # 'use_label_encoder=False' and 'eval_metric' are set to avoid deprecation warnings
    model = xgb.XGBClassifier(objective='multi:softmax', num_class=len(class_names),
                              use_label_encoder=False, eval_metric='mlogloss', n_jobs=-1, random_state=42)

    # Train the model
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Evaluate performance
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ XGBoost Accuracy: {accuracy:.4f}\n")

    print("📊 Classification Report:")
    report_dict = classification_report(y_test, y_pred, target_names=class_names, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report_dict).transpose()
    print(report_df)

    # Save the trained model
    joblib.dump(model, 'ids_xgb_model.pkl')
    print("\n💾 XGBoost model saved to 'ids_xgb_model.pkl'")

    # Visualize the Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title('Confusion Matrix for XGBoost Model')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.tight_layout()
    plt.show()


# --- Main execution block ---
if __name__ == "__main__":
    print("🔹 Loading preprocessed data from 'train_test_data.pkl'...")
    try:
        X_train, X_test, y_train, y_test = joblib.load('train_test_data.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
        class_names = label_encoder.classes_
    except FileNotFoundError:
        print("Error: Required .pkl files not found. Please run data_preprocessing.py first.")
        exit()

    print("Data loaded successfully.")

    train_and_evaluate_xgboost(X_train, y_train, X_test, y_test, class_names)

    print("\n✅ XGBoost training and evaluation complete!")