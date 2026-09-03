import os
# import openai # Uncomment this if you pip install openai and have an API key

def generate_explanation(risk_score: int, flags: list) -> str:
    """
    Generates a human-readable explanation of the document's fraud risk.
    Acts as a mock LLM for the MVP, but can be easily swapped for a real API.
    """
    
    # --- REAL LLM API IMPLEMENTATION (Commented out for MVP) ---
    # openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
    # prompt = f"A document verification system gave a risk score of {risk_score}/100. Flags: {', '.join(flags)}. Explain this to a user in 2 sentences."
    # try:
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[{"role": "user", "content": prompt}]
    #     )
    #     return response.choices[0].message.content
    # except Exception as e:
    #     return f"LLM API Error: {e}"
    
    # --- MOCK LLM IMPLEMENTATION (Use this for now) ---
    if risk_score == 0 and not flags:
        return "The document appears to be entirely authentic. No suspicious visual, text, or metadata anomalies were detected."
    
    flag_text = ", ".join(flags)
    
    if risk_score < 40:
        return f"This document has a low risk score of {risk_score}. However, note the following minor issues: {flag_text}. Proceed with standard verification."
        
    elif risk_score < 70:
        return f"Warning: This document generated a moderate risk score of {risk_score}. Multiple suspicious elements were detected, specifically: {flag_text}. Manual review is recommended."
        
    else:
        return f"Critical Alert: High probability of document fraud (Score: {risk_score}). Major red flags triggered: {flag_text}. Do not accept this document without severe scrutiny."