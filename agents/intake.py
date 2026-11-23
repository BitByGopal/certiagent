"""Intake agent: image -> OCR text (Tesseract)."""
import os
from pathlib import Path
import pytesseract
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
if os.getenv("TESSERACT_CMD") and os.path.exists(os.getenv("TESSERACT_CMD")):
    pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")

# Language file kept inside the project (no admin rights needed)
LOCAL_TESSDATA = Path(__file__).resolve().parent.parent / "tessdata"
if (LOCAL_TESSDATA / "eng.traineddata").exists():
    os.environ["TESSDATA_PREFIX"] = str(LOCAL_TESSDATA)
    OCR_CONFIG = f"--tessdata-dir {LOCAL_TESSDATA.as_posix()} --psm 4"
else:
    OCR_CONFIG = "--psm 4"
print(f"[intake] OCR config: {OCR_CONFIG}")


def run(image: Image.Image) -> dict:
    gray = image.convert("L")
    text = pytesseract.image_to_string(gray, config=OCR_CONFIG)
    data = pytesseract.image_to_data(gray, config=OCR_CONFIG, output_type=pytesseract.Output.DICT)
    confs = [float(c) for c, w in zip(data["conf"], data["text"]) if w.strip() and float(c) >= 0]
    mean_conf = sum(confs) / len(confs) if confs else 0.0
    return {"ocr_text": text, "ocr_confidence": round(mean_conf, 1)}