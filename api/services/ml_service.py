import joblib
import pandas as pd
import numpy as np
import logging
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
from api.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Define feature columns in exact order
FEATURE_COLUMNS = [
    'month', 'month_sin', 'month_cos', 'is_summer', 'is_holiday_month', 'is_weekend',
    'region_southeast', 'region_northeast', 'region_midwest', 'region_alaska',
    'region_pacific_west', 'region_intermountain', 'region_national_capital', 'region_other'
]

# Load artifacts on module load
try:
    model = joblib.load(Path(settings.model_path))
    label_encoder = joblib.load(Path(settings.encoder_path))
    thresholds_df = pd.read_csv(Path(settings.thresholds_path))
    logger.info("ML model, encoder, and thresholds loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load ML artifacts: {e}")
    model = None
    label_encoder = None
    thresholds_df = None

async def predict_crowd(
    park_code: str,
    month: int,
    day_of_week: int,  # 0=Monday, 6=Sunday
    region: str,
    temperature_f: float = 65.0
) -> Dict[str, Any]:
    """
    Predicts crowd level for a given park and time.
    """
    if model is None or label_encoder is None or thresholds_df is None:
        return {
            "crowd_label": "Unknown",
            "confidence": 0.0,
            "error": "ML service not initialized"
        }

    try:
        # 1. Validation: Check if park exists in thresholds
        if park_code not in thresholds_df['park_code'].values:
            logger.warning(f"Park code {park_code} not found in thresholds.")
            return {
                "crowd_label": "Unknown",
                "confidence": 0.0,
                "park_code": park_code
            }

        # 2. Feature Engineering
        month_sin = math.sin(2 * math.pi * month / 12)
        month_cos = math.cos(2 * math.pi * month / 12)
        is_summer = 1 if month in [6, 7, 8] else 0
        is_holiday_month = 1 if month in [7, 11, 12] else 0
        is_weekend = 1 if day_of_week >= 5 else 0

        # One-hot encode region
        # Normalize region input to match feature columns
        region_norm = region.lower().replace(" ", "_")
        
        # Mapping common variations if needed (heuristic based on GEMINI.md)
        region_map = {
            "southeast": "southeast",
            "northeast": "northeast",
            "midwest": "midwest",
            "alaska": "alaska",
            "pacific_west": "pacific_west",
            "intermountain": "intermountain",
            "national_capital": "national_capital"
        }
        
        target_region = region_map.get(region_norm, "other")
        
        features = {
            'month': month,
            'month_sin': month_sin,
            'month_cos': month_cos,
            'is_summer': is_summer,
            'is_holiday_month': is_holiday_month,
            'is_weekend': is_weekend,
            'region_southeast': 1 if target_region == "southeast" else 0,
            'region_northeast': 1 if target_region == "northeast" else 0,
            'region_midwest': 1 if target_region == "midwest" else 0,
            'region_alaska': 1 if target_region == "alaska" else 0,
            'region_pacific_west': 1 if target_region == "pacific_west" else 0,
            'region_intermountain': 1 if target_region == "intermountain" else 0,
            'region_national_capital': 1 if target_region == "national_capital" else 0,
            'region_other': 1 if target_region == "other" else 0
        }

        # 3. Create DataFrame and Predict
        X = pd.DataFrame([features])[FEATURE_COLUMNS]
        
        prediction_idx = model.predict(X)[0]
        probabilities = model.predict_proba(X)[0]
        
        # 4. Decode Label
        crowd_label = label_encoder.inverse_transform([prediction_idx])[0]
        # Map numeric labels to human-readable strings if needed
        LABEL_MAP = {0: "Low", 1: "Moderate", 2: "High", 3: "Very High",
                     "0": "Low", "1": "Moderate", "2": "High", "3": "Very High"}
        crowd_label = LABEL_MAP.get(crowd_label, str(crowd_label))
        confidence = float(np.max(probabilities))
        
        # 5. Build probabilities dict
        prob_dict = {}
        for idx, prob in enumerate(probabilities):
            readable_label = LABEL_MAP.get(idx, str(idx))
            prob_dict[readable_label] = round(float(prob), 3)

        return {
            "crowd_label": str(crowd_label),
            "confidence": round(confidence, 3),
            "probabilities": prob_dict,
            "park_code": park_code
        }

    except Exception as e:
        logger.error(f"Prediction error for {park_code}: {e}")
        return {
            "crowd_label": "Unknown",
            "confidence": 0.0,
            "park_code": park_code,
            "error": str(e)
        }
