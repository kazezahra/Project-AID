from pathlib import Path
from datetime import datetime


class PDFReportGenerator:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.output_dir = self.project_root / "reports"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, prediction_result, report_text):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"autism_screening_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        content = f"""AUTISM PRE-SCREENING ASSESSMENT REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

RESULTS
Q-CHAT Score: {prediction_result.get('qchat_score')}/10
Risk Level: {prediction_result.get('qchat_risk_level')}
Model Confidence: {prediction_result.get('model_probability_asd')*100:.1f}%

ASSESSMENT
{report_text}

DISCLAIMER
This is a screening tool only, not a diagnosis. Professional evaluation is required."""
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        return filepath


_pdf_generator = None


def get_pdf_generator():
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = PDFReportGenerator()
    return _pdf_generator


def generate_pdf_report(prediction_result, report_text):
    generator = get_pdf_generator()
    return generator.generate(prediction_result, report_text)
