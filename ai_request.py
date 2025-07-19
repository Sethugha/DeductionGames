
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
#print("Available Models:", available_models)


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
                Solution as dictionary using keys: 
                culprit: The villain
                method: How the crime was done
                evidence: The clue details leading to this deduction
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()

        # Validiere und verarbeite die Antwort
        result = json.loads(response_text)
        return (result)


    def ai_hint_request(self, data_string, clue):
        """
        Order information about a clue or suspect.
        """
        prompt = f"""
                Answer every question as if you never heard of it even 
                if it´s a repetition from an older question.
                Based on {data_string}, tell me details about {clue}
                but do not mention the final purpose.
                Answer in english
                
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        #Validiere und verarbeite die Antwort
        #result = json.loads(response_text)

        return (response_text)

    def ai_character_request(self, data_string, character):
        """
        Order information about a clue or suspect.
        """
        prompt = f"""
                Answer every question as if you never heard of it even 
                if it´s a repetition from an older question.
                Based on {data_string}, tell me details about {character}
                but do not tell if he´s the culprit or not.
                Answer in english

                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        # Validiere und verarbeite die Antwort
        # result = json.loads(response_text)

        return (response_text)


    def ai_interrogation(self, data_string, character, clue):
        """
        Order information about a clue or suspect.
        """
        prompt = f"""
                Based on {data_string}, you are the character {character}.
                The interrogator asks you about {clue}.
                You cannot lie but if you are the culprit, 
                you are interested in covering up your participation.
                Answer in english
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        # Validiere und verarbeite die Antwort
        # result = json.loads(response_text)

        return (response_text)


    def ai_accusation(self, data_string, character, evidences):
        """
        Accusing a suspect you present the evidences you found.
        The culprit will give up.
        """
        prompt = f"""
                Based on {data_string}, you are the character {character}.
                The interrogator accuses you to be the culprit and presents the evidences {evidences}.
                If the evidences cover more than 80% of the real happening, 
                the character will confess method and motive of the crime.
                If the character is not the culprit,
                the character will laugh the investigator down.
                Answer in english.  
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        # Validiere und verarbeite die Antwort
        # result = json.loads(response_text)
        return (response_text)


    def search_indicators(self, data_string, search_str):
        """
        Accusing a suspect you present the evidences you found.
        The culprit will give up.
        """
        prompt = f"""
                        Based on {data_string}, reveal
                        details which are part of the original text
                        and match at least the nouns contained in 
                        {search_str}.
                        Answer in english.
                        """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        # Validiere und verarbeite die Antwort
        # result = json.loads(response_text)
        return (response_text)
