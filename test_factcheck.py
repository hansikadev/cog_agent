import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from services.schemas import ExtractedClaim
from services.verifier import verify_claim

def main():
    print("Testing Fact-Check Logic using Gemini & Tavily...")
    
    # Check for API Keys
    tavily_key = os.environ.get("TAVILY_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if not tavily_key or tavily_key == "your_tavily_api_key_here":
        print("❌ Warning: TAVILY_API_KEY is not set or invalid.")
    else:
        print("✅ TAVILY_API_KEY is loaded.")
        
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        print("❌ Warning: GEMINI_API_KEY is not set or invalid.")
    else:
        print("✅ GEMINI_API_KEY is loaded.")

    # Create a mock claim
    test_claim = ExtractedClaim(
        claim_text="The global artificial intelligence market size was valued at USD 136.55 billion in 2022.",
        claim_type="Market Size",
        entities=["artificial intelligence", "global market"],
        value="136.55 billion",
        year="2022"
    )
    
    print(f"\nEvaluating Claim: '{test_claim.claim_text}'")
    
    # Run the verification
    result = verify_claim(test_claim)
    
    print("\n--- VERIFICATION RESULT ---")
    print(f"Status: {result.status.value}")
    print(f"Confidence Score: {result.confidence_score}")
    print(f"Explanation: {result.explanation}")
    print(f"Correct Value: {result.correct_value}")
    
    if result.evidence_sources:
        print("\nSources found by Tavily:")
        for ev in result.evidence_sources:
            print(f"- {ev.source_title} ({ev.source_url})")
    else:
        print("No evidence sources found.")
        
if __name__ == "__main__":
    main()
