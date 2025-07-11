
"""
ai_request.py - Interface to Google Gemini AI
"""
import os
import json
import requests
from typing import Optional, Dict, List
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# Lade Umgebungsvariablen
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# Konfiguriere die Google AI
generation_config = GenerationConfig(
    temperature=0.9,
    top_p=1,
    top_k=1,
    max_output_tokens=2048,
)

genai.configure(api_key=API_KEY)

# List available models an pick the right one
available_models = [m.name for m in genai.list_models()]
print("Available Models:", available_models)




class AIRequest():
    """
    Schnittstelle zur Google Gemini AI für game creation
    """
    def __init__(self):
        try:
            # use "models/gemini-2.0-flash"
            self.model = genai.GenerativeModel(
                "models/gemini-2.0-flash",
                generation_config=generation_config
            )
            print("AI-Modell successful initialized")
        except Exception as e:
            print(f"Error initializing AI model: {str(e)}")
            raise

    def ai_request(self, data_string: str) -> Dict:
        """
        Order the metamorphosis.
        """
        prompt = f"""
                Answer every question as if you never heard of it even if it´s a repetition from an older question.
                Based on {data_string}, generate an interactive deduction game scenario.
                Provide a brief introduction to the case (3–4 sentences).
                List the characters involved (include suspects and witnesses).
                List them as list of dictionaries see example below:          
                Provide 5–7 clues that the player can investigate, some relevant, some misleading.                                
                The clues should be detailed enough for some logical deduction, but not necessary lead to the solution.
                User should go deeper into the details to find the solution.
                At last append the solution. 
                Answer in json as follows:
                case_title: a telling name.
                Case description: Brief description
                Characters as list of dictionaries with keys name and role
                Clues as list of dictionaries, keys are clue_name, description and details
                questions as list,
                Solution as dictionary using keys: 
                culprit: The villain
                method: How the crime was done
                evidence: The clue details leading to this deduction
                
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        print(response_text)
        # Validiere und verarbeite die Antwort
        result = json.loads(response_text)

        return (result)
