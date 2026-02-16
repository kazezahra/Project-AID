"""
PDF Report Generation Module
"""

from pathlib import Path
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class PDFReportGenerator:
    """Generate professional PDF reports"""
    
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.output_dir = self.project_root / "reports"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate(self, prediction_result, report_text):
        """Generate PDF report"""
        if not HAS_REPORTLAB:
            return self._create_text_report(prediction_result, report_text)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"autism_screening_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        try:
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.75*inch,
                bottomMargin=0.75*inch
            )
            
            story = self._build_story(prediction_result, report_text)
            doc.build(story)
            print(f"✓ PDF generated: {filepath}")
            return filepath
        
        except Exception as e:
            print(f"PDF generation error: {e}")
            return self._create_text_report(prediction_result, report_text)
    
    def _build_story(self, prediction_result, report_text):
        """Build PDF content"""
        story = []
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#6fb0b7'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        
        # Title
        story.append(Paragraph("AUTISM PRE-SCREENING ASSESSMENT", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Results table
        risk = prediction_result.get('qchat_risk_level')
        score = prediction_result.get('qchat_score')
        prob = prediction_result.get('model_probability_asd')
        
        results_data = [
            ["Q-CHAT Score", f"{score}/10"],
            ["Risk Level", risk],
            ["Confidence", f"{prob*100:.1f}%"]
        ]
        
        results_table = Table(results_data)
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0fafb')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#ddd')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(results_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Report
        story.append(Paragraph("CLINICAL ASSESSMENT", styles['Heading2']))
        story.append(Paragraph(report_text.replace('\n', '<br/>'), styles['Normal']))
        
        return story
    
    def _create_text_report(self, prediction_result, report_text):
        """Create text report fallback"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"autism_screening_{timestamp}.txt"
        filepath = self.output_dir / filename
        
        content = f"""AUTISM PRE-SCREENING ASSESSMENT REPORT
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

RESULTS
=======
Q-CHAT Score: {prediction_result.get('qchat_score')}/10
Risk Level: {prediction_result.get('qchat_risk_level')}
Model Confidence: {prediction_result.get('model_probability_asd')*100:.1f}%

ASSESSMENT
==========
{report_text}

DISCLAIMER
==========
This is a screening tool, not a diagnosis. Professional evaluation is required.
"""
        
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
