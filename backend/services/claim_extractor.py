import os
import json
from groq import Groq
from backend.services.schemas import ExtractedClaim

MODEL_NAME = "llama-3.3-70b-versatile" 

def extract_claims_from_text(text: str) -> list[ExtractedClaim]:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        print("Warning: Missing Groq API Key. Returning mock claims.")
        return [
            ExtractedClaim(claim_text="The Earth revolves around the Sun.", claim_type="Quantitative", entities=["Earth", "Sun"]),
            ExtractedClaim(claim_text="In 2025, over 99.8% of all Fortune 500 CEOs were replaced by artificial intelligence agents.", claim_type="Statistic", entities=["Fortune 500", "AI"], year="2025")
        ]
        
    client = Groq(api_key=api_key)
    prompt = f"""
    You are an expert data extractor and fact checker. 
    Analyze the following text and extract all quantitative claims, statistics, percentages, 
    dates, financial numbers, technical metrics, market size claims, rankings, and measurable statements.
    
    Return the result strictly as a JSON object with a single key "claims" containing an array of objects. Each object should have:
    - claim_text (string): The exact quote or tightly paraphrased claim.
    - claim_type (string): e.g., "Statistic", "Percentage", "Financial", "Market Size", "Ranking".
    - entities (array of strings): Key entities or companies involved.
    - value (string): The main numerical value.
    - year (string): The relevant year if mentioned, else null.
    
    If no claims are found, return {{"claims": []}}.
    
    TEXT:
    {text}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that outputs JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=MODEL_NAME,
            response_format={"type": "json_object"},
        )
        
        data = json.loads(response.choices[0].message.content)
        claims = [ExtractedClaim(**item) for item in data.get("claims", [])]
        return claims
    except Exception as e:
        print(f"Error extracting claims: {e}")
        return []
