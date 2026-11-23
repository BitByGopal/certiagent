"""Streamlit demo.  Run:  streamlit run app.py"""
import streamlit as st
from PIL import Image
from graph import verify
from agents.llm import llm_available, MODEL

st.set_page_config(page_title="CertiAgent", page_icon="🎓", layout="wide")
st.title("🎓 CertiAgent — Multi-Agent Certificate Verifier")
st.caption("SIH25029 · Authenticity Validator for Academia · LangGraph + Gemini · synthetic data only")

with st.sidebar:
    mode = st.radio("Extraction / reasoning", ["llm", "rules"], format_func=lambda m: f"LLM ({MODEL})" if m == "llm" else "Rules baseline")
    if mode == "llm" and not llm_available():
        st.warning("No GEMINI_API_KEY in .env — falling back to rules.")
    st.info("Upload images from data/certificates. Never upload a real person's certificate.")

file = st.file_uploader("Upload a certificate image", type=["png", "jpg", "jpeg"])
if file:
    img = Image.open(file).convert("RGB")
    with st.spinner("Agents working: intake → extraction → registry + forensics → reasoning ..."):
        out = verify(img, mode)
    colour = {"GENUINE": "green", "FAKE": "red", "REVIEW": "orange"}[out["verdict"]]
    st.markdown(f"## Verdict: :{colour}[{out['verdict']}]") 
    st.write(out["explanation"])

    c1, c2 = st.columns(2)
    c1.image(img, caption="Uploaded certificate", use_container_width=True)
    c2.image(out["ela_map"], caption=f"ELA map · score {out['forensics']['ela_score']} (threshold {out['forensics']['threshold']})", use_container_width=True)

    a, b, c = st.columns(3)
    with a:
        st.subheader("1 · Extraction")
        st.caption(f"mode: {out['extraction_mode']} · OCR confidence {out['ocr_confidence']}")
        st.json(out["fields"])
    with b:
        st.subheader("2 · Registry")
        st.metric("Status", out["registry"]["status"])
        if out["registry"]["mismatches"]: st.table(out["registry"]["mismatches"])
    with c:
        st.subheader("3 · Evidence")
        for e in out["evidence"] or ["No problems found."]: st.write("•", e)
    with st.expander("Raw OCR text"):
        st.text(out["ocr_text"])
