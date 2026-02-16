"""
ML Model Inference Module
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
import os

# Get correct project root path
# This file is at autism-prescreening-tool/src/inference.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Try multiple possible model locations
possible_model_dirs = [
    PROJECT_ROOT / "models",  # autism-prescreening-tool/models
    PROJECT_ROOT / "autism-prescreening-tool" / "models",  # autism-prescreening-tool/autism-prescreening-tool/models
    Path(os.getenv("MODELS_DIR", "")) if os.getenv("MODELS_DIR") else None,
]

MODELS_DIR = None
for model_dir in possible_model_dirs:
    if model_dir and model_dir.exists():
        MODELS_DIR = model_dir
        break

if not MODELS_DIR:
    # Set to first option as fallback (will error in _load_model with helpful message)
    MODELS_DIR = possible_model_dirs[0]

print(f"[Inference] Project root: {PROJECT_ROOT}")
print(f"[Inference] Models dir: {MODELS_DIR}")
print(f"[Inference] Models dir exists: {MODELS_DIR.exists()}")


class AutismPredictor:
    """Load and use the trained autism prediction model"""
    
    def __init__(self):
        self.model = None
        self.threshold_config = None
        self.model_path = MODELS_DIR / "calibrated_model.joblib"
        self.threshold_path = MODELS_DIR / "threshold_config.joblib"
        print(f"[Predictor] Model path: {self.model_path}")
        print(f"[Predictor] Threshold path: {self.threshold_path}")
        self._load_model()
    
    def _load_model(self):
        """Load the trained model from disk"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found at {self.model_path}")
            if not self.threshold_path.exists():
                raise FileNotFoundError(f"Threshold not found at {self.threshold_path}")
            
            self.model = joblib.load(str(self.model_path))
            self.threshold_config = joblib.load(str(self.threshold_path))
            print(f"✓ Model loaded successfully")
        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            raise
    
    def prepare_features(self, data):
        """Convert user responses to model input format - returns DataFrame as expected by model"""
        qchat_answers = data.get("qchat_answers", {})
        qchat_features = []
        
        # Convert A/B/C/D/E to binary (A=1, others=0)
        for i in range(1, 11):
            answer = qchat_answers.get(i) or qchat_answers.get(str(i))
            value = 1 if str(answer).upper() == "A" else 0
            qchat_features.append(value)
        
        # Metadata features - handle multiple input formats
        age_mons = int(data.get("age_mons", 24))
        
        # Handle sex - can be integer (1/0), string ("male"/"female"), or boolean
        sex_val = data.get("sex", 0)
        if isinstance(sex_val, str):
            sex = 1 if sex_val.lower() in ["male", "m", "1", "yes"] else 0
        else:
            sex = 1 if int(sex_val) == 1 else 0
        
        # Handle jaundice - can be integer (1/0), string ("yes"/"no"), or boolean
        jaundice_val = data.get("jaundice", 0)
        if isinstance(jaundice_val, str):
            jaundice = 1 if jaundice_val.lower() in ["yes", "y", "1", "true"] else 0
        else:
            jaundice = 1 if int(jaundice_val) == 1 else 0
        
        # Handle family history - can be integer (1/0), string ("yes"/"no"), or boolean
        family_asd_val = data.get("family_mem_with_asd", 0)
        if isinstance(family_asd_val, str):
            family_asd = 1 if family_asd_val.lower() in ["yes", "y", "1", "true"] else 0
        else:
            family_asd = 1 if int(family_asd_val) == 1 else 0
        
        # Create DataFrame with proper column names (as model expects them)
        features_dict = {
            'a1': qchat_features[0], 'a2': qchat_features[1], 'a3': qchat_features[2],
            'a4': qchat_features[3], 'a5': qchat_features[4], 'a6': qchat_features[5],
            'a7': qchat_features[6], 'a8': qchat_features[7], 'a9': qchat_features[8],
            'a10': qchat_features[9], 'age_mons': age_mons, 'sex': sex, 
            'jaundice': jaundice, 'family_mem_with_asd': family_asd
        }
        
        df = pd.DataFrame([features_dict])
        print(f"[Features] DataFrame prepared with columns: {list(df.columns)}")
        print(f"[Features] Values: {df.values[0]}")
        return df
    
    def predict(self, data):
        """Make prediction on input data"""
        try:
            X = self.prepare_features(data)
            
            # Get probability
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba(X)[0]
                asd_probability = float(probabilities[1])
            else:
                asd_probability = float(self.model.predict(X)[0])
            
            threshold = float(self.threshold_config.get("threshold", 0.5))
            
            # Risk level
            if asd_probability >= threshold:
                risk_level = "High"
            elif asd_probability >= threshold * 0.65:
                risk_level = "Medium"
            else:
                risk_level = "Low"
            
            # Q-CHAT score
            qchat_answers = data.get("qchat_answers", {})
            qchat_score = sum(
                1 for i in range(1, 11)
                if str(qchat_answers.get(i) or qchat_answers.get(str(i))).upper() == "A"
            )
            
            interpretation = self._get_interpretation(risk_level, qchat_score)
            
            result = {
                "model_probability_asd": asd_probability,
                "risk_threshold": threshold,
                "qchat_score": int(qchat_score),
                "qchat_risk_level": risk_level,
                "qchat_referral_interpretation": interpretation,
                "disclaimer": "This is a screening tool, not a diagnostic test. Professional evaluation is strongly recommended."
            }
            
            print(f"[Prediction] Result: {result}")
            return result
        
        except Exception as e:
            print(f"❌ Prediction error: {e}")
            raise ValueError(f"Prediction failed: {str(e)}")
    
    def _get_interpretation(self, risk_level, qchat_score):
        if risk_level == "High":
            return f"Score {qchat_score}/10: Significant autism characteristics. Professional evaluation strongly recommended."
        elif risk_level == "Medium":
            return f"Score {qchat_score}/10: Some autism characteristics. Professional consultation recommended."
        else:
            return f"Score {qchat_score}/10: Lower autism characteristics. Monitor development."


_predictor = None


def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = AutismPredictor()
    return _predictor


def predict_autism_risk(data):
    predictor = get_predictor()
    return predictor.predict(data)
