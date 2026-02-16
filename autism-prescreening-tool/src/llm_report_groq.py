import os
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


class ReportGenerator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if HAS_GROQ and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except:
                pass
    
    def generate_report(self, prediction_result):
        if self.client:
            try:
                risk = prediction_result.get("qchat_risk_level")
                score = prediction_result.get("qchat_score")
                return f"AUTISM PRE-SCREENING ASSESSMENT\n\nQ-CHAT Score: {score}/10\nRisk Level: {risk}\n\nThis screening assessment indicates {risk.lower()} risk characteristics. Professional evaluation by a qualified healthcare provider is strongly recommended for accurate diagnosis."
            except:
                pass
        return self._template_report(prediction_result)
    
    def _template_report(self, result):
        return f"""AUTISM PRE-SCREENING ASSESSMENT

Q-CHAT Score: {result.get('qchat_score')}/10
Risk Level: {result.get('qchat_risk_level')}

INTERPRETATION
{result.get('qchat_referral_interpretation')}

DISCLAIMER
This is a screening tool only, not a diagnosis. Professional evaluation by qualified healthcare professionals is required."""

_generator = None

def get_generator():
    global _generator
    if _generator is None:
        _generator = ReportGenerator()
    return _generator

def generate_risk_report(prediction_result):
    generator = get_generator()
    return generator.generate_report(prediction_result)
