import os
from dotenv import load_dotenv
load_dotenv()

from backend.services.claim_extractor import extract_claims_from_text
from backend.services.pdf_service import extract_text_from_pdf

with open("dummy_claims.pdf", "rb") as f:
    text = extract_text_from_pdf(f.read())
    
print("EXTRACTED TEXT FROM PDF:")
print(text)
print("-" * 50)

print("CALLING LLM...")
claims = extract_claims_from_text(text)
print("EXTRACTED CLAIMS:")
for c in claims:
    print(c)
