"""Shared Gemini client with a simple retry for free-tier rate limits (HTTP 429)."""
import os, time
from dotenv import load_dotenv
from google import genai

load_dotenv()
# On Streamlit Cloud the key comes from "Secrets" instead of .env
try:
    import streamlit as st
    for k in ("GEMINI_API_KEY", "GEMINI_MODEL"):
        if k in st.secrets and not os.getenv(k):
            os.environ[k] = str(st.secrets[k])
except Exception:
    pass
_client = None

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def llm_available() -> bool:
    key = os.getenv("GEMINI_API_KEY", "")
    return bool(key) and key != "paste_your_key_here"


def client() -> genai.Client:
    global _client
    if _client is None:
        from google.genai import types
        _client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options=types.HttpOptions(api_version="v1beta"),
        )
    return _client


def generate(contents, config=None, retries: int = 4):
    """Call Gemini; on a rate-limit error wait and try again."""
    wait = 8
    for attempt in range(retries):
        try:
            return client().models.generate_content(model=MODEL, contents=contents, config=config)
        except Exception as e:  # google.genai.errors.APIError carries the HTTP code
            if ("429" in str(e) or "RESOURCE_EXHAUSTED" in str(e)) and attempt < retries - 1:
                print(f"[llm] rate limited, waiting {wait}s ...")
                time.sleep(wait); wait *= 2
                continue
            raise
