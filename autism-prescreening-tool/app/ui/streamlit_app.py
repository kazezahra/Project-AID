import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st

from src.inference import predict_autism_risk
from src.llm_report_groq import generate_risk_report
from src.pdf_generator import generate_pdf_report


st.set_page_config(
    page_title="Autism Pre-Screening Tool (Q-CHAT-10)",
    page_icon="🧩",
    layout="centered"
)

st.title("🧩 Autism Pre-Screening Tool (Q-CHAT-10)")
st.caption("Screening tool for parents/guardians. Not a medical diagnosis.")

st.divider()


# -------------------------------
# Parent Metadata Form
# -------------------------------
st.subheader("Step 1: Child Information")

age_mons = st.number_input("Age (in months)", min_value=12, max_value=60, value=24)

sex = st.selectbox("Sex", ["male", "female"])

jaundice = st.selectbox("History of Jaundice?", ["no", "yes"])

family_mem_with_asd = st.selectbox("Family member with ASD?", ["no", "yes"])


st.divider()


# -------------------------------
# QCHAT Questions
# -------------------------------
st.subheader("Step 2: Q-CHAT-10 Questionnaire")

st.write("Select the best answer (A–E) for each question.")

ANSWER_OPTIONS = ["A", "B", "C", "D", "E"]

qchat_answers = {}

for i in range(1, 11):
    qchat_answers[i] = st.selectbox(
        f"Q{i}: Select Answer",
        ANSWER_OPTIONS,
        key=f"q{i}"
    )


st.divider()


# -------------------------------
# Submit + Prediction
# -------------------------------
if st.button("🔍 Run Screening", type="primary"):

    payload = {
        "age_mons": int(age_mons),
        "sex": sex,
        "jaundice": jaundice,
        "family_mem_with_asd": family_mem_with_asd,
        "qchat_answers": qchat_answers
    }

    with st.spinner("Running screening model..."):
        result = predict_autism_risk(payload)

    st.success("Screening completed!")

    st.subheader("📌 Results")

    st.write(f"**Q-CHAT Score:** {result['qchat_score']}/10")
    st.write(f"**Risk Level (UI):** {result['qchat_risk_level']}")
    st.write(f"**Standard Interpretation:** {result['qchat_referral_interpretation']}")

    st.write("---")

    st.write(f"**Model Probability (ASD traits):** `{result['model_probability_asd']:.4f}`")

    default_decision = result["prediction_default_threshold_0_50"]
    tuned_decision = result["prediction_screening_threshold"]

    st.write(f"**Default Threshold (0.50):** {default_decision['label']}")
    st.write(f"**Screening Threshold ({tuned_decision['threshold']:.4f}):** {tuned_decision['label']}")

    st.info(result["disclaimer"])

    # Store in session for report generation
    st.session_state["inference_result"] = result


st.divider()


# -------------------------------
# Generate Report
# -------------------------------
st.subheader("Step 3: Generate Risk Assessment Report")

if "inference_result" not in st.session_state:
    st.warning("Run screening first to generate a report.")
else:
    if st.button("📝 Generate Report (Groq LLM)"):

        with st.spinner("Generating report using Groq LLM..."):
            report_text = generate_risk_report(st.session_state["inference_result"])

        st.session_state["report_text"] = report_text
        st.success("Report generated successfully!")

    if "report_text" in st.session_state:
        st.text_area("Generated Report", st.session_state["report_text"], height=350)


st.divider()


# -------------------------------
# PDF Download
# -------------------------------
st.subheader("Step 4: Download PDF")

if "report_text" not in st.session_state:
    st.warning("Generate the report first to download PDF.")
else:
    if st.button("📄 Generate PDF"):

        with st.spinner("Creating PDF report..."):
            pdf_path = generate_pdf_report(
                st.session_state["inference_result"],
                st.session_state["report_text"]
            )

        st.session_state["pdf_path"] = pdf_path
        st.success("PDF generated!")

    if "pdf_path" in st.session_state:
        pdf_path = st.session_state["pdf_path"]

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="⬇️ Download PDF Report",
                data=f,
                file_name=pdf_path.name,
                mime="application/pdf"
            )
