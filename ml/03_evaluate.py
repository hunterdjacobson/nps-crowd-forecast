import pandas as pd
import joblib
import xgboost as xgb
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Paths
BASE_DIR = Path(__file__).parent.parent
FEATURES_PATH = BASE_DIR / "data" / "processed" / "features.csv"
MODEL_PATH = BASE_DIR / "api" / "models" / "crowd_model.joblib"
ENCODER_PATH = BASE_DIR / "api" / "models" / "label_encoder.joblib"
IMPORTANCE_PATH = BASE_DIR / "data" / "processed" / "feature_importances.csv"

def evaluate():
    # 1. Load Model and Encoder
    print(f"Loading model from {MODEL_PATH}...")
    model = joblib.load(MODEL_PATH)
    
    print(f"Loading encoder from {ENCODER_PATH}...")
    le = joblib.load(ENCODER_PATH)

    # 2. Load and Split Data (Same as training)
    print(f"Loading features from {FEATURES_PATH}...")
    df = pd.read_csv(FEATURES_PATH)
    
    X = df.drop(columns=['park_code', 'crowd_label'])
    y = df['crowd_label']
    
    # Use the same split parameters as ml/02_train.py
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    # 3. Predict
    print("Making predictions on test set...")
    y_pred = model.predict(X_test)
    y_test_encoded = le.transform(y_test)

    # 4. Metrics
    acc = accuracy_score(y_test_encoded, y_pred)
    print(f"\nOverall Accuracy: {acc:.4f}")

    target_names = ['Low', 'Moderate', 'High', 'Very High']
    print("\nClassification Report:")
    print(classification_report(y_test_encoded, y_pred, target_names=target_names))

    # 5. Confusion Matrix
    cm = confusion_matrix(y_test_encoded, y_pred)
    cm_df = pd.DataFrame(
        cm, 
        index=[f"Actual {name}" for name in target_names],
        columns=[f"Pred {name}" for name in target_names]
    )
    print("\nConfusion Matrix (DataFrame):")
    print(cm_df)

    # 6. Feature Importances
    if IMPORTANCE_PATH.exists():
        print("\nTop 10 Features:")
        importances = pd.read_csv(IMPORTANCE_PATH)
        print(importances.head(10))
    else:
        print("\nFeature importance file not found.")

if __name__ == "__main__":
    evaluate()
