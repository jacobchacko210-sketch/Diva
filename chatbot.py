import ollama

def get_chatbot_response(user_message: str, document_context: dict = None) -> str:
    """
    Sends the user's message and the document's risk context to the Ollama model.
    """
    
    # 1. Define the System Prompt
    system_instruction = """You are DIVA, a specialized Document Intelligence & Verification Assistant.

                            Your sole purpose is to educate and answer questions about different types of identity documents, government credentials, and official cards (such as Passports, Driver's Licenses, Aadhaar, PAN Cards, Voter IDs, Residence Permits, etc., across both Indian and international jurisdictions).

                        Core Responsibilities:
                        1. Explain Document Types: Detail the purpose, issuing authorities, standard field layouts, and standard design specifications for requested document types.
                        2. Detail Security Features: Explain physical and digital security mechanisms, including Guilloche line patterns, microprinting, ghost portraits, UV features, holographic overlays, machine-readable zones (MRZ), QR codes, and PDF417 barcodes.
                        3. Identify Common Irregularities: Clarify typical signs of tampering, font inconsistencies, demographic mismatches, and structural layout defects.
                        4. Objective and Direct: Answer user questions directly without refusing queries about unfamiliar, foreign, or synthetic test documents. If a document format is queried, provide its recognized real-world layout, standard issuing criteria, and security benchmarks.
                        5. Keep explanations concise, structured, and informative.
                        """

    # 2. Inject the Document Context (if a document was just scanned)
    if document_context:
        system_instruction += "\n\nContext of the currently uploaded document:\n"
        system_instruction += f"- Final Risk Score: {document_context.get('risk_score', 'N/A')}/100\n"
        system_instruction += f"- Triggered Flags: {', '.join(document_context.get('flags', ['None']))}\n"
        system_instruction += f"- Extracted Text Snippet: {document_context.get('extracted_text', 'None')[:200]}...\n"

    # 3. Call the local Ollama instance
    try:
        response = ollama.chat(
            model='gpt-oss:20b-cloud',
            messages=[
                {'role': 'system', 'content': system_instruction},
                {'role': 'user', 'content': user_message}
            ]
        )
        return response['message']['content']
        
    except Exception as e:
        return f"Chatbot Error: Make sure the Ollama application is running in the background and the model is pulled. Details: {e}"