"""
Flask API for Autism Pre-Screening Tool
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import traceback

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

print(f"[App] Project root: {PROJECT_ROOT}")
print(f"[App] Python path: {sys.path[:2]}")

try:
    from src.inference import predict_autism_risk
    from src.llm_report_groq import generate_risk_report
    from src.pdf_generator import generate_pdf_report
    print("[App] ✓ All modules imported successfully")
except Exception as e:
    print(f"[App] ❌ Import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

app = Flask(__name__)
CORS(app, origins="*")

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Autism Pre-Screening API"
    }), 200

@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Predict autism risk"""
    try:
        data = request.get_json()
        print(f"\n[API] POST /api/predict")
        print(f"[API] Received: {data}")
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        required = ["age_mons", "gender", "jaundice", "family_mem_with_asd", "qchat_answers"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400
        
        # Validate qchat_answers
        qchat = data.get("qchat_answers", {})
        if len(qchat) != 10:
            return jsonify({
                "error": f"Expected 10 answers, got {len(qchat)}"
            }), 400
        
        # Convert string keys to int
        qchat_int = {}
        for k, v in qchat.items():
            try:
                qchat_int[int(k)] = v
            except ValueError:
                qchat_int[int(k) if isinstance(k, str) else k] = v
        
        data["qchat_answers"] = qchat_int
        
        # Run prediction
        print("[API] Running prediction...")
        result = predict_autism_risk(data)
        
        print(f"[API] ✓ Prediction successful")
        print(f"[API] Result: {result}\n")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[API] ❌ Error: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-report", methods=["POST"])
def api_generate_report():
    try:
        data = request.get_json()
        
        if not data or "prediction_result" not in data:
            return jsonify({"error": "Missing prediction_result"}), 400
        
        result = data["prediction_result"]
        report_text = generate_risk_report(result)
        
        return jsonify({
            "status": "success",
            "report": report_text
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-pdf", methods=["POST"])
def api_generate_pdf():
    try:
        data = request.get_json()
        
        if not data or "prediction_result" not in data or "report_text" not in data:
            return jsonify({"error": "Missing fields"}), 400
        
        result = data["prediction_result"]
        report_text = data["report_text"]
        
        pdf_path = generate_pdf_report(result, report_text)
        
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
        
        return pdf_data, 200, {
            "Content-Type": "application/pdf",
            "Content-Disposition": f"attachment; filename={pdf_path.name}"
        }
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/questions", methods=["GET"])
def api_get_questions():
    questions = [
        {"id": 1, "question": "Does your child make and maintain eye contact?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 2, "question": "Does your child respond to their name when called?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 3, "question": "Does your child engage in back-and-forth interaction?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 4, "question": "Does your child point to share interest?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 5, "question": "Does your child use gestures?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 6, "question": "Does your child babble or use speech sounds?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 7, "question": "Does your child imitate sounds or words?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 8, "question": "Does your child show interest in playing?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 9, "question": "Does your child adapt to changes?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]},
        {"id": 10, "question": "Does your child show typical sensory response?", "options": ["Always", "Usually", "Sometimes", "Rarely", "Never"]}
    ]
    return jsonify({"questions": questions}), 200

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 AUTISM PRE-SCREENING TOOL API")
    print("="*60)
    print("Starting Flask server...")
    print("URL: http://0.0.0.0:5000")
    print("="*60 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=True)
