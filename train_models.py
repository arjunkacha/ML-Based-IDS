import joblib
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


def train_and_evaluate(model, model_name, X_train, y_train, X_test, y_test, class_names):
    """
    A helper function to train a model and print its evaluation metrics.
    """
    print(f"--- Training {model_name} ---")

    # Train the model
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Evaluate performance
    accuracy = accuracy_score(y_test, y_pred)
    print(f"✅ Accuracy: {accuracy:.4f}\n")

    print("📊 Classification Report:")
    print(classification_report(y_test, y_pred, target_names=class_names, zero_division=0))

    # Visualize the Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=class_names, yticklabels=class_names)
    plt.title(f'Confusion Matrix for {model_name}')
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.show()


# --- Main execution block ---
if __name__ == "__main__":
    # 1. Load the preprocessed data
    print("🔹 Loading preprocessed data from 'train_test_data.pkl'...")
    try:
        X_train, X_test, y_train, y_test = joblib.load('train_test_data.pkl')
        label_encoder = joblib.load('label_encoder.pkl')
        class_names = label_encoder.classes_
    except FileNotFoundError:
        print("Error: Required .pkl files not found. Please run data_preprocessing.py first.")
        exit()

    print("Data loaded successfully.")

    # 2. Initialize and run Decision Tree
    # We use class_weight='balanced' to help with the imbalanced dataset.
    dt_model = DecisionTreeClassifier(random_state=42, class_weight='balanced')
    train_and_evaluate(dt_model, "Decision Tree", X_train, y_train, X_test, y_test, class_names)

    # 3. Initialize and run Random Forest
    # n_jobs=-1 uses all available CPU cores for faster training.
    rf_model = RandomForestClassifier(random_state=42, class_weight='balanced', n_jobs=-1)
    train_and_evaluate(rf_model, "Random Forest", X_train, y_train, X_test, y_test, class_names)

    print("✅ Model training and evaluation complete!")

    # 4. Save the best performing model (Random Forest)
    print("\n🔹 Saving the trained Random Forest model...")
    joblib.dump(rf_model, 'ids_rf_model.pkl')
    print("✅ Model saved to 'ids_rf_model.pkl'")

    print("\n✅ Process complete!")