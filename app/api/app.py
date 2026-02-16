"""
Flask API for Autism Pre-Screening Tool
"""

from flask import Flask, request, jsonify
import json
from datetime import datetime
import os
from flask_cors import CORS
import sys
from pathlib import Path
import traceback
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get correct path - app.py is at Downloads/autism-prescreening-tool/app/api/app.py
# We need to go up 3 levels to get to Downloads/autism-prescreening-tool/
SCRIPT_DIR = Path(__file__).resolve().parent  # app/api
APP_DIR = SCRIPT_DIR.parent  # app
PROJECT_ROOT = APP_DIR.parent  # autism-prescreening-tool (the one with app, frontend, src)

print(f"[Flask] Script location: {SCRIPT_DIR / 'app.py'}")
print(f"[Flask] Project root: {PROJECT_ROOT}")

# Add both the root and src directories to path
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Also add the nested project folder for backward compatibility
nested_project = PROJECT_ROOT / "autism-prescreening-tool"
if nested_project.exists():
    sys.path.insert(0, str(nested_project))
    sys.path.insert(0, str(nested_project / "src"))

print(f"[Flask] Python path: {sys.path[:4]}")

# Import after path is set
try:
    from src.inference import predict_autism_risk
    from src.llm_report_groq import generate_risk_report
    # Import the root `src/pdf_generator.py` explicitly to avoid ambiguous nested imports
    import importlib.util
    pdf_mod_path = PROJECT_ROOT / "src" / "pdf_generator.py"
    spec = importlib.util.spec_from_file_location("root_pdf_generator", str(pdf_mod_path))
    pdf_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pdf_mod)
    generate_pdf_report = getattr(pdf_mod, "generate_pdf_report")
    print("[Flask] ✓ All modules imported successfully (pdf_generator loaded from root src)")
except Exception as e:
    print(f"[Flask] ❌ Import failed: {e}")
    traceback.print_exc()
    raise

app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST"], allow_headers=["Content-Type"])


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Autism Pre-Screening API",
        "version": "1.0.0"
    }), 200


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Predict autism risk"""
    try:
        data = request.get_json()
        print(f"\n[API] POST /api/predict")
        print(f"[API] Received: {data}")

        # Write incoming request to log for debugging frontend payloads
        try:
            logs_dir = PROJECT_ROOT / "logs"
            os.makedirs(str(logs_dir), exist_ok=True)
            log_path = logs_dir / "predict_requests.log"
            with open(str(log_path), "a", encoding="utf-8") as lf:
                lf.write(json.dumps({
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "remote": request.remote_addr,
                    "payload": data
                }, ensure_ascii=False) + "\n")
        except Exception as _logerr:
            print(f"[API] Warning: failed to write predict log: {_logerr}")
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate all required fields
        required = ["age_mons", "sex", "jaundice", "family_mem_with_asd", "qchat_answers"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400
        
        # Validate qchat_answers has 10 entries
        qchat = data.get("qchat_answers", {})
        if len(qchat) != 10:
            return jsonify({
                "error": f"Expected 10 Q-CHAT answers, got {len(qchat)}"
            }), 400
        
        # Convert to correct format
        if isinstance(list(qchat.keys())[0], str):
            qchat_int = {int(k): v for k, v in qchat.items()}
            data["qchat_answers"] = qchat_int
        
        # Run prediction
        result = predict_autism_risk(data)
        print(f"[API] ✓ Prediction successful\n")

        # Log result for debugging
        try:
            with open(str(PROJECT_ROOT / "logs" / "predict_requests.log"), "a", encoding="utf-8") as lf:
                lf.write(json.dumps({
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "remote": request.remote_addr,
                    "payload": data,
                    "result": result
                }, ensure_ascii=False) + "\n")
        except Exception as _logerr:
            print(f"[API] Warning: failed to write prediction result to log: {_logerr}")
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[API] ❌ Error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-report", methods=["POST"])
def api_generate_report():
    """Generate detailed report from prediction result"""
    try:
        data = request.get_json()
        print(f"\n[API] POST /api/generate-report")
        print(f"[API] Received: {data}")
        
        if not data or "prediction_result" not in data:
            return jsonify({"error": "Missing prediction_result"}), 400
        
        prediction_result = data["prediction_result"]
        print(f"[API] Generating report for result: {prediction_result}")
        
        report_text = generate_risk_report(prediction_result)
        print(f"[API] ✓ Report generated successfully")
        
        return jsonify({
            "status": "success",
            "report": report_text
        }), 200
        
    except Exception as e:
        print(f"[API] ❌ Report generation error: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/generate-pdf", methods=["POST"])
def api_generate_pdf():
    """Generate PDF report"""
    try:
        data = request.get_json()
        
        if not data or "prediction_result" not in data or "report_text" not in data:
            return jsonify({"error": "Missing prediction_result or report_text"}), 400

        # Log incoming PDF generation request
        try:
            logs_dir = PROJECT_ROOT / "logs"
            os.makedirs(str(logs_dir), exist_ok=True)
            pdf_log = logs_dir / "pdf_requests.log"
            with open(str(pdf_log), "a", encoding="utf-8") as pf:
                pf.write(json.dumps({
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "remote": request.remote_addr,
                    "payload_summary": {
                        "has_prediction": "prediction_result" in data,
                        "report_length": len(str(data.get("report_text", "")))
                    }
                }, ensure_ascii=False) + "\n")
        except Exception as _e:
            print(f"[API] Warning: failed to write pdf request log: {_e}")

        result = data["prediction_result"]
        report_text = data["report_text"]

        pdf_path = generate_pdf_report(result, report_text)

        # Verify file exists and size
        try:
            if not pdf_path or not Path(str(pdf_path)).exists():
                return jsonify({"error": "PDF generation failed - file not created"}), 500
            file_size = Path(str(pdf_path)).stat().st_size
            # Log file path and size
            with open(str(pdf_log), "a", encoding="utf-8") as pf:
                pf.write(json.dumps({
                    "ts": datetime.utcnow().isoformat() + "Z",
                    "pdf_path": str(pdf_path),
                    "size": file_size
                }, ensure_ascii=False) + "\n")

        except Exception as _e:
            print(f"[API] Warning: failed to verify/write pdf log: {_e}")

        with open(str(pdf_path), "rb") as f:
            pdf_data = f.read()

        return pdf_data, 200, {
            "Content-Type": "application/pdf",
            "Content-Disposition": f"attachment; filename={Path(str(pdf_path)).name}"
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/questions", methods=["GET"])
def api_get_questions():
    """Get Q-CHAT-10 questions"""
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
    print(f"Running on http://0.0.0.0:5000")
    print("="*60 + "\n")
    
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
