
"""
ai_request.py - Interface to Google Gemini AI
"""
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig

# Load environment vars
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# Configurate Google AI
generation_config = GenerationConfig(
    temperature=0.2,
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
            self.chat = self.model.start_chat()
            print("AI-Model successful initialized")
        except Exception as e:
            print(f"Error initializing AI model: {str(e)}")
            raise

    def metamorphosis(self, data_string):
        """
        Order the metamorphosis.
        """
        prompt = f"""
                You are a script author ordered to create a script for a deduction game
                out of the given crime story {data_string}.
                Your complete knowledge about events, evidences and facts arises from the crime story itself.
                You must not use any knowledge not included in the story.
                You must not make own deductions.
                
                Create a json object as visible below:
                'title': extracted story title or a telling case title.
                'introduction': Short description of the crime case (about 5-7 sentences).
                'characters': Extract the persons contained in {data_string} and deliver a list of dicts,
                each containing the full name using key 'name' and the person´s role in the story using key'role'.
                'clues': a list of dictionaries as described below:
                Every item, occurrence or witness linked to the crime is to store into 
                'clue_name': name.
                'clue_description': A brief description of the clue and its possible connection o the crime.
                'clue_details': A list containing 3 significant attributes pointing to the crime.
                afterwards extend the clue list 
                'solution': The perpetrator´s full name.
                'method': The method how the crime was done matching the story as exactly as possible.
                'evidences': A list of clue names which are pointing to the crime.
                extent the clue list by 3-4 red herrings styled exactly like the real clues.       
                
                While creating the ip
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
                You are the investigator in the field. You have studied the known facts
                they gave you but you examine the crime site hoping to find
                additional details of {clue}.
                You must not leave the story frame.
                Every additional examination of a clue reveals up to 2 new details if these
                are mentioned within {data_string}.
                Create an answer in plain english as if it came from an observer
                informing You afterwards about your findings. 
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
                You are an actor playing an aquaintance of {character} 
                from the crime story {data_string}. Your complete knowledge is restricted
                to events and facts described in this crime story.
                You must not use any knowledge from outside or draw own conclusions.
                Answer directly without hedging the questions.
                Your task is to play the role authentical, not to "win" the interrogation.
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        # Validiere und verarbeite die Antwort
        # result = json.loads(response_text)

        return (response_text)


    def ai_interrogation(self, data_string, character, clue, solution):
        """
        Order information about a clue or suspect.
        """
        prompt = f"""
                You are an actor playing the character {character.name} 
                from the crime story {data_string}. Your complete knowledge is restricted
                to events and facts described in this crime story.
                You must not use any knowledge from outside or draw own conclusions.
                Your task is to play the role authentical, not to "win" the interrogation.
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        # Validiere und verarbeite die Antwort
        # result = json.loads(response_text)

        return (response_text)


    def ai_accusation(self, data_string, character, evidences, solution):
        """
        Accusing a suspect you present the evidences you found.
        The culprit will give up.
        """
        prompt = f"""
                You are an actor playing the character {character.name} 
                from the crime story {data_string}, accused of the crime and 
                confronted with the evidences {evidences}. Your complete knowledge is restricted
                to events and facts described in this crime story.
                You must not use any knowledge from outside or draw own conclusions.
                Your task is to play the role authentical, not to "win" the interrogation.
                If the evidences cover about 50% of the facts, break down and confess.
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        # Validiere und verarbeite die Antwort
        # result = json.loads(response_text)
        return (response_text)


    def search_indicators(self, data_string, search_str, clue):
        """
        Look for additional indicators at a crime scene.
        """
        prompt = f"""
                        You are the investigator, looking for indicators 
                        which could deliver additional information about {clue}.
                        Details which are part of {data_string} and are 
                        associated with {clue} should match the gist of {search_str} to be mentioned.
                        If there is no match simply answer like:
                        'Nothing special caught your eye'.  
                        Answer in english.
                        """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
        return (response_text)
