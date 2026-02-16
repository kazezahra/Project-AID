from src.inference import predict_autism_risk
from src.llm_report_groq import generate_risk_report


sample_payload = {
    "age_mons": 28,
    "sex": "male",
    "jaundice": "no",
    "family_mem_with_asd": "yes",
    "qchat_answers": {
        1: "A",
        2: "C",
        3: "B",
        4: "D",
        5: "C",
        6: "A",
        7: "E",
        8: "B",
        9: "C",
        10: "B"
    }
}

result = predict_autism_risk(sample_payload)
report = generate_risk_report(result)

print("\n" + "="*80)
print(report)
print("="*80)
