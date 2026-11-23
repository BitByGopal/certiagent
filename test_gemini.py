"""Step 1: check that your Gemini key works.  Run:  python test_gemini.py"""
import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
resp = client.models.generate_content(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    contents="Reply with exactly: CertiAgent connected",
)
print(resp.text)
