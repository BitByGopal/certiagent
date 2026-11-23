"""Reasoning agent: fuse evidence -> verdict (fixed rules) + explanation (Gemini, grounded on the evidence only)."""
import json
from google.genai import types
from .llm import generate, llm_available

LOW_OCR_CONFIDENCE = 60.0


def decide(registry: dict, forensics: dict, ocr_conf: float):
    evidence = []
    if registry["status"] == "NOT_FOUND":
        evidence.append("No matching record in the institution registry.")
    for m in registry["mismatches"]:
        evidence.append(f"{m['field']} on certificate is '{m['certificate']}' but registry has '{m['registry']}'.")
    if forensics["suspicious"]:
        evidence.append(f"ELA score {forensics['ela_score']} exceeds threshold {forensics['threshold']} (possible local edit).")
    if ocr_conf < LOW_OCR_CONFIDENCE:
        evidence.append(f"Low OCR confidence ({ocr_conf}); fields may be misread.")

    if registry["status"] == "MATCH" and not forensics["suspicious"]:
        verdict = "GENUINE" if ocr_conf >= LOW_OCR_CONFIDENCE else "REVIEW"
    elif registry["status"] == "MATCH":
        verdict = "REVIEW"                       # only forensics fired
    elif ocr_conf < LOW_OCR_CONFIDENCE:
        verdict = "REVIEW"                       # mismatch may just be a bad scan
    else:
        verdict = "FAKE"
    return verdict, evidence


EXPLAIN = """You are the Reasoning Agent of a certificate verification system.
The verdict has already been decided by fixed rules: {verdict}.
Write 2-3 plain sentences for a human verifier explaining this verdict.
Use ONLY the evidence below. Do not add facts, numbers or names that are not in it.
If the verdict is REVIEW, say what the person should check manually.
Evidence: {evidence}"""


def run(registry: dict, forensics: dict, ocr_conf: float, use_llm: bool = True) -> dict:
    verdict, evidence = decide(registry, forensics, ocr_conf)
    explanation = " ".join(evidence) or "All checks passed: registry record matches and no image anomalies were found."
    if use_llm and llm_available():
        try:
            resp = generate(EXPLAIN.format(verdict=verdict, evidence=json.dumps(evidence)),
                            config=types.GenerateContentConfig(temperature=0.2))
            explanation = resp.text.strip()
        except Exception as e:
            print(f"[reasoning] LLM failed ({e}); using evidence list")
    return {"verdict": verdict, "evidence": evidence, "explanation": explanation}
