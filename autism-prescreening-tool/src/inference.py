import joblib
import numpy as np
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = PROJECT_ROOT / "models"

print(f"[Inference] Project root: {PROJECT_ROOT}")
print(f"[Inference] Models dir: {MODELS_DIR}")
print(f"[Inference] Models dir exists: {MODELS_DIR.exists()}")

# Column names as they were used during training
FEATURE_COLUMNS = ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9', 'a10', 
                   'age_mons', 'sex', 'jaundice', 'family_mem_with_asd']


class AutismPredictor:
    def __init__(self):
        self.model = None
        self.threshold_config = None
        self.model_path = MODELS_DIR / "calibrated_model.joblib"
        self.threshold_path = MODELS_DIR / "threshold_config.joblib"
        
        print(f"[Predictor] Model path: {self.model_path}")
        print(f"[Predictor] Model exists: {self.model_path.exists()}")
        print(f"[Predictor] Threshold path: {self.threshold_path}")
        print(f"[Predictor] Threshold exists: {self.threshold_path.exists()}")
        
        self._load_model()
    
    def _load_model(self):
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model not found: {self.model_path}")
            if not self.threshold_path.exists():
                raise FileNotFoundError(f"Threshold not found: {self.threshold_path}")
            
            self.model = joblib.load(str(self.model_path))
            self.threshold_config = joblib.load(str(self.threshold_path))
            print(f"✓ Models loaded successfully")
            
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def prepare_features(self, data):
        """Convert A/B/C/D/E to binary (A=1, others=0) and create DataFrame"""
        qchat_answers = data.get("qchat_answers", {})
        qchat_features = []
        
        # Convert each answer to binary
        for i in range(1, 11):
            answer = qchat_answers.get(i) or qchat_answers.get(str(i))
            value = 1 if str(answer).upper() == "A" else 0
            qchat_features.append(value)
            print(f"  Q{i}: {answer} → {value}")
        
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
        print(f"[Features] DataFrame shape: {df.shape}, Columns: {list(df.columns)}")
        print(f"[Features] Values: {df.values}")
        return df
    
    def predict(self, data):
        """Make prediction"""
        try:
            print("[Predict] Starting...")
            X_df = self.prepare_features(data)
            
            # Get probability
            print("[Predict] Calling model.predict_proba()...")
            if hasattr(self.model, "predict_proba"):
                proba = self.model.predict_proba(X_df)
                print(f"[Predict] Probabilities shape: {proba.shape}")
                print(f"[Predict] Probabilities: {proba}")
                asd_probability = float(proba[0][1])
            else:
                print("[Predict] Model doesn't have predict_proba, using predict()...")
                asd_probability = float(self.model.predict(X_df)[0])
            
            threshold = float(self.threshold_config.get("threshold", 0.5))
            print(f"[Predict] ASD Prob: {asd_probability:.4f}, Threshold: {threshold:.4f}")
            
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
            
            result = {
                "model_probability_asd": asd_probability,
                "risk_threshold": threshold,
                "qchat_score": int(qchat_score),
                "qchat_risk_level": risk_level,
                "qchat_referral_interpretation": f"Score: {qchat_score}/10. Risk Level: {risk_level}.",
                "disclaimer": "This is a screening tool, not a diagnosis. Professional evaluation is required."
            }
            
            print(f"[Predict] ✓ Result: {result}")
            return result
        
        except Exception as e:
            print(f"[Predict] ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Prediction failed: {str(e)}")


_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = AutismPredictor()
    return _predictor

def predict_autism_risk(data):
    predictor = get_predictor()
    return predictor.predict(data)


_predictor = None

def get_predictor():
    global _predictor
    if _predictor is None:
        _predictor = AutismPredictor()
    return _predictor

def predict_autism_risk(data):
    predictor = get_predictor()
    return predictor.predict(data)
