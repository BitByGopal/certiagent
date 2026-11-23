# CertiAgent — Multi-Agent Authenticity Validator (SIH25029)

Five agents in a LangGraph graph: **Intake (OCR) → Extraction (Gemini, structured JSON) → Registry check ∥ ELA forensics → Reasoning (verdict + Gemini explanation)**.

## Setup
1. Install Tesseract OCR (Windows: UB Mannheim installer) and note the path to `tesseract.exe`.
2. `python -m venv venv` then activate it (`venv\Scripts\activate` on Windows).
3. `pip install -r requirements.txt`
4. Copy `.env.example` to `.env`, paste your key from aistudio.google.com, and check `TESSERACT_CMD`.
5. `python test_gemini.py` → should print *CertiAgent connected*.

## Run
- `python generate_data.py` – creates `data/registry.csv` and 60 test certificates
- `python graph.py data/certificates/000_genuine.png` – verify one file in the terminal
- `streamlit run app.py` – demo UI
- `python evaluate.py rules` then `python evaluate.py llm` – numbers for the presentation

Synthetic data only. Do not upload real certificates: free-tier Gemini inputs may be used by Google to improve its products.
