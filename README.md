# Autism Pre-Screening Tool (Project-AID)

A Final Year Project implementing an intelligent autism pre-screening tool for toddlers using machine learning and natural language processing.

## 📋 Overview

This project combines the Q-CHAT-10 questionnaire with machine learning and large language models to provide:

- **Q-CHAT-10 Scoring**: Automated scoring of the Quick Chat Autism Test (10 questions)
- **ML Classification**: XGBoost model predicting autism spectrum disorder traits
- **AI-Powered Reports**: LLM-generated screening reports using Groq API
- **PDF Export**: Professional PDF report generation with ReportLab
- **Web UI**: Interactive Flask backend + HTML/CSS frontend

## ✨ Features

- ✅ Parent-friendly Q-CHAT-10 questionnaire interface
- ✅ Automatic scoring with risk level classification
- ✅ ML-based probability predictions for ASD traits
- ✅ AI-generated screening assessment reports
- ✅ Downloadable PDF reports with detailed findings
- ✅ Model calibration and threshold tuning
- ✅ Cross-validation and performance metrics

## 🛠 Tech Stack

- **Backend**: Flask, CORS
- **ML**: scikit-learn, XGBoost, pandas, numpy
- **AI/LLM**: Groq API (Llama 3.1)
- **Frontend**: HTML5, CSS3, JavaScript
- **Reports**: ReportLab (PDF generation)
- **Environment**: Python 3.8+

## 📁 Project Structure

```
autism-prescreening-tool/
├── app/
│   └── api/
│       ├── app.py              # Flask backend
│       └── requirements.txt
├── frontend/
│   └── AID-FYP/
│       ├── index.html          # Main interface
│       ├── questionnaire.html   # Q-CHAT-10 form
│       └── styles.css
├── autism-prescreening-tool/
│   ├── src/
│   │   ├── inference.py            # Model prediction
│   │   ├── scoring.py              # Q-CHAT-10 scoring
│   │   ├── llm_report_groq.py      # LLM report generation
│   │   ├── pdf_generator.py        # PDF export
│   │   ├── model_training.py       # Model training
│   │   └── calibrate_and_tune_threshold.py
│   ├── models/
│   │   ├── best_model.joblib
│   │   ├── calibrated_model.joblib
│   │   └── threshold_config.joblib
│   ├── data/
│   │   ├── raw/                # Raw dataset
│   │   └── processed/          # Processed training data
│   └── notebooks/              # Jupyter notebooks
├── .env                        # Environment variables (not in repo)
├── requirements.txt
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Groq API key (get from https://console.groq.com)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/kazezahra/Project-AID.git
cd autism-prescreening-tool
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
Create a `.env` file in the project root:
```env
GROQ_API_KEY=your_groq_api_key_here
FLASK_ENV=development
FLASK_DEBUG=1
```

5. **Start the backend**
```bash
cd app/api
python app.py
```
Backend will run on `http://localhost:5000`

6. **Start the frontend** (in a new terminal)
```bash
cd frontend/AID-FYP
python -m http.server 8000
```
Access the UI at `http://localhost:8000/index.html`

## 📊 How It Works

### 1. Q-CHAT-10 Assessment
- Parent answers 10 quick questions about child behavior
- Each answer is scored (0-1)
- Total score determines initial risk level

### 2. ML Prediction
- Q-CHAT responses fed to XGBoost model
- Model outputs probability of autism traits
- Probability combined with Q-CHAT score

### 3. LLM Report Generation
- Q-CHAT score, ML probability, and demographics sent to Groq API
- Llama 3.1 generates detailed assessment report
- Report includes:
  - Risk assessment summary
  - Key findings and recommendations
  - Next steps for consultation

### 4. PDF Export
- Final report formatted as professional PDF
- Includes all assessment data and recommendations
- Downloadable by clinician/parent

## 📈 Model Details

- **Dataset**: Toddler Autism Dataset (July 2018)
- **Features**: 10 Q-CHAT questions (binary/ternary responses)
- **Algorithm**: XGBoost classifier with calibration
- **Performance**: Cross-validated with multiple random splits
- **Threshold**: Tuned for optimal sensitivity/specificity balance

## 🔧 Configuration

### Model Parameters
Edit `autism-prescreening-tool/src/config.py`:
```python
MODEL_PATH = "models/best_model.joblib"
CALIBRATED_MODEL_PATH = "models/calibrated_model.joblib"
THRESHOLD_CONFIG_PATH = "models/threshold_config.joblib"
```

### API Endpoints

**POST /screen**
- Input: Q-CHAT responses, demographics
- Output: Risk assessment + PDF report

**POST /report/text**
- Input: Assessment data
- Output: LLM-generated text report

## 📋 Example Usage

```bash
# Run inference on saved model
python autism-prescreening-tool/src/test_inference.py

# Generate a sample report
python autism-prescreening-tool/src/test_pdf_report.py

# Test LLM report generation
python autism-prescreening-tool/src/test_llm_report_groq.py
```

## ⚠️ Important Notes

- **API Key Security**: Store your Groq API key in `.env` (never commit to GitHub)
- **Model Accuracy**: This tool is for pre-screening only, not diagnosis
- **Clinical Use**: Requires supervision by qualified healthcare professional
- **Data Privacy**: No data is stored; responses are processed and discarded

## 🧪 Testing

Run tests to validate the setup:

```bash
# Test inference module
python autism-prescreening-tool/src/test_inference.py

# Test PDF generation
python autism-prescreening-tool/src/test_pdf_report.py

# Test LLM integration
python autism-prescreening-tool/src/test_llm_report_groq.py
```

## 🐳 Docker Deployment

Build and run with Docker:
```bash
docker-compose up --build
```
This will start both backend and frontend services.

## 📚 Documentation

See additional documentation:
- [Architecture](ARCHITECTURE.md) - System design overview
- [Integration Guide](INTEGRATION_GUIDE.md) - API endpoints and workflows
- [Testing Guide](TESTING_GUIDE.md) - Test procedures
- [Deployment](DEPLOYMENT_CHECKLIST.md) - Production deployment steps

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and open a Pull Request

## 📝 License

This project is part of a Final Year Project. See LICENSE for details.

## � Authors

**Kaneez e Zahra** - Project Lead & Development  
**Umer Khalid** - Backend & API Development  
**Wardah Haya** - Frontend & UI/UX  

Final Year Project - Data Science & AI

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Last Updated**: February 2026  
**Version**: 1.0.0
