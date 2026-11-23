from agents.extraction import extract_llm
from agents.llm import llm_available, MODEL

print("Key loaded:", llm_available(), "| Model:", MODEL)

sample = """Ranchi Institute of Technology
PROVISIONAL DEGREE CERTIFICATE
This is to certify that
Riya Nair
has been awarded the degree of Bachelor of Science
Roll Number: 2025119
Year of Passing: 2024
CGPA: 7.74
Certificate ID: JH597183"""

print(extract_llm(sample))