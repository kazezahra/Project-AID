"""
LLM Report Generation using Groq API
"""

import os
from dotenv import load_dotenv

load_dotenv()

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


class ReportGenerator:
    """Generate AI-powered reports using Groq LLM"""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        
        if HAS_GROQ and self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                print(f"Groq initialization warning: {e}")
    
    def generate_report(self, prediction_result):
        """Generate detailed report from prediction results"""
        if self.client:
            try:
                return self._generate_with_llm(prediction_result)
            except Exception as e:
                print(f"LLM generation failed: {e}")
                return self._generate_template_report(prediction_result)
        else:
            return self._generate_template_report(prediction_result)
    
    def _generate_with_llm(self, result):
        """Generate report using Groq LLM"""
        try:
            risk = result.get("qchat_risk_level")
            score = result.get("qchat_score")
            interp = result.get("qchat_referral_interpretation")
            
            prompt = f"""Write a brief clinical assessment report for an autism screening with:
- Q-CHAT Score: {score}/10
- Risk Level: {risk}
- Interpretation: {interp}

Keep it under 200 words and professional."""
            
            message = self.client.messages.create(
                model="mixtral-8x7b-32768",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"[LLM] Error with Groq API: {e}")
            raise
    
    def _generate_template_report(self, result):
        """Fallback template-based report"""
        risk = result.get("qchat_risk_level", "Unknown")
        score = result.get("qchat_score", 0)
        interp = result.get("qchat_referral_interpretation", "")
        
        return f"""AUTISM PRE-SCREENING ASSESSMENT REPORT
        
SCREENING RESULTS
Q-CHAT Score: {score}/10
Risk Level: {risk}
Interpretation: {interp}

RECOMMENDATIONS
{self._get_recommendations(risk)}

DISCLAIMER
This screening tool is NOT a diagnosis. Professional evaluation by qualified healthcare 
professionals (developmental pediatrician, clinical psychologist, speech-language pathologist) 
is required for accurate diagnosis of Autism Spectrum Disorder.

Always consult with your healthcare provider for comprehensive assessment."""
    
    def _get_recommendations(self, risk_level):
        """Get recommendations based on risk level"""
        if risk_level == "High":
            return """• Urgent referral to developmental pediatrician
• Comprehensive autism diagnostic evaluation
• Speech and language pathology assessment
• Early intervention services consultation"""
        elif risk_level == "Medium":
            return """• Consultation with developmental specialist
• Formal developmental assessment
• Speech and language evaluation
• Follow-up screening in 3-6 months"""
        else:
            return """• Continue monitoring development
• Routine pediatric check-ups
• Monitor achievement of developmental milestones
• Contact provider if concerns arise"""


_generator = None


def get_generator():
    global _generator
    if _generator is None:
        _generator = ReportGenerator()
    return _generator


def generate_risk_report(prediction_result):
    generator = get_generator()
    return generator.generate_report(prediction_result)
