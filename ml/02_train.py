import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
import optuna
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report

# Paths
BASE_DIR = Path(__file__).parent.parent
FEATURES_PATH = BASE_DIR / "data" / "processed" / "features.csv"
MODELS_DIR = BASE_DIR / "api" / "models"
MODEL_SAVE_PATH = MODELS_DIR / "crowd_model.joblib"
ENCODER_SAVE_PATH = MODELS_DIR / "label_encoder.joblib"
IMPORTANCE_PATH = BASE_DIR / "data" / "processed" / "feature_importances.csv"

# Ensure models directory exists
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def train():
    # 1. Load data
    print(f"Loading features from {FEATURES_PATH}...")
    df = pd.read_csv(FEATURES_PATH)
    
    # Separate features and label
    # Drop park_code as it's not a numeric feature for XGBoost in this setup (unless we encoded it, which we didn't)
    X = df.drop(columns=['park_code', 'crowd_label'])
    y = df['crowd_label']
    
    feature_names = X.columns.tolist()
    print(f"Features: {feature_names}")

    # 2. Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    print(f"Train set size: {X_train.shape[0]}, Test set size: {X_test.shape[0]}")

    # 3. Label Encoder
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    y_test_encoded = le.transform(y_test)
    
    joblib.dump(le, ENCODER_SAVE_PATH)
    print(f"Label encoder saved to {ENCODER_SAVE_PATH}")

    # 4. Optuna hyperparameter search
    def objective(trial):
        params = {
            'max_depth': trial.suggest_int('max_depth', 3, 10),
            'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.3, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 100, 800),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
            'tree_method': 'hist',
            'eval_metric': 'mlogloss',
            'random_state': 42
        }
        
        clf = xgb.XGBClassifier(**params)
        
        # 3-fold CV
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
        score = cross_val_score(clf, X_train, y_train_encoded, cv=skf, scoring='accuracy').mean()
        return score

    print("Starting Optuna search (30 trials)...")
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=30)

    print(f"Best CV accuracy: {study.best_value:.4f}")
    print(f"Best params: {study.best_params}")

    # 5. Retrain on FULL training set
    print("Retraining final model on full training set...")
    best_params = study.best_params
    best_params['tree_method'] = 'hist'
    best_params['eval_metric'] = 'mlogloss'
    best_params['random_state'] = 42
    
    final_model = xgb.XGBClassifier(**best_params)
    final_model.fit(X_train, y_train_encoded)

    # 6. Evaluate on test set
    y_pred = final_model.predict(X_test)
    test_acc = accuracy_score(y_test_encoded, y_pred)
    print(f"Final Test Accuracy: {test_acc:.4f}")
    
    target_names = ['Low', 'Moderate', 'High', 'Very High']
    print("\nClassification Report:")
    print(classification_report(y_test_encoded, y_pred, target_names=target_names))

    # 7. Save model
    joblib.dump(final_model, MODEL_SAVE_PATH)
    print(f"Model saved to {MODEL_SAVE_PATH}")

    # 8. Feature Importances
    importances = final_model.feature_importances_
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values(by='importance', ascending=False)
    
    importance_df.to_csv(IMPORTANCE_PATH, index=False)
    print(f"Feature importances saved to {IMPORTANCE_PATH}")

if __name__ == "__main__":
    train()
