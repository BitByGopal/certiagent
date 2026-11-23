"""Extraction agent: OCR text -> structured fields.
mode="llm"   : Gemini with a Pydantic schema (structured JSON output)
mode="rules" : regex baseline used in the CA1 paper (also the fallback if no API key)
"""
import re
from typing import Optional
from pydantic import BaseModel, Field
from google.genai import types
from .llm import generate, llm_available


class CertificateFields(BaseModel):
    university: Optional[str] = Field(None, description="Issuing university name")
    name: Optional[str] = Field(None, description="Full name of the certificate holder")
    roll: Optional[str] = Field(None, description="Roll number, digits only")
    program: Optional[str] = Field(None, description="Degree awarded")
    year: Optional[str] = Field(None, description="Year of passing, 4 digits")
    cgpa: Optional[str] = Field(None, description="CGPA with two decimals, e.g. 8.25")
    cert_id: Optional[str] = Field(None, description="Certificate ID such as JH123456, no spaces")


PROMPT = """You are the Extraction Agent in a certificate verification system.
Read the OCR text of an academic certificate and fill the schema.
Rules:
- Copy values exactly as they appear; fix only obvious OCR spacing (e.g. 'JH 12 3456' -> 'JH123456').
- If a field is missing or unreadable, return null. NEVER guess or invent a value.
OCR text:
\"\"\"{text}\"\"\""""


def extract_llm(text: str) -> dict:
    import json
    resp = generate(
        PROMPT.format(text=text) + "\nReturn ONLY a JSON object with keys: "
        "university, name, roll, program, year, cgpa, cert_id (use null if missing).",
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0,
        ),
    )
    raw = (resp.text or "").strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(raw)
    data = {k: (None if v is None else str(v)) for k, v in data.items()}
    return CertificateFields.model_validate(data).model_dump()


PATTERNS = {
    "roll": r"Roll\s*Number\s*[:;]?\s*([0-9]{5,9})",
    "year": r"Year\s*of\s*Passing\s*[:;]?\s*(20[0-9]{2})",
    "cgpa": r"CGPA\s*[:;]?\s*([0-9][.,][0-9]{2})",
    "cert_id": r"Certificate\s*I[Dd0]\s*[:;]?\s*(JH\s*[0-9]{6})",
}


def extract_rules(text: str) -> dict:
    out = {k: None for k in CertificateFields.model_fields}
    for k, p in PATTERNS.items():
        m = re.search(p, text, re.I)
        if m:
            out[k] = m.group(1).replace(" ", "").replace(",", ".")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    for i, l in enumerate(lines):
        if re.search(r"certify\s+that", l, re.I) and i + 1 < len(lines):
            out["name"] = lines[i + 1]
            break
    out["university"] = lines[0] if lines else None
    return out


def run(ocr_text: str, mode: str = "llm") -> dict:
    if mode == "llm" and llm_available():
        try:
            return {"fields": extract_llm(ocr_text), "extraction_mode": "llm"}
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"[extraction] LLM failed ({e}); using rules")
    return {"fields": extract_rules(ocr_text), "extraction_mode": "rules"}