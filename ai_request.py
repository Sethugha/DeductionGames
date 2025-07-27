
"""
ai_request.py - Interface to Google Gemini AI
"""
import os
import json
from flask import jsonify
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import storage
from data_models import db, AIConfig, Conversation

# Load environment vars
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
ai_config = storage.retrieve_aiconfig_by_status()
AI_CONFIG_COUNT = ai_config.id

# Configurate Google AI
generation_config = GenerationConfig(
    temperature=ai_config.ai_temperature,
    top_p=ai_config.ai_top_p,
    top_k=ai_config.ai_top_k,
    max_output_tokens=ai_config.ai_max_out
)

genai.configure(api_key=API_KEY)

# List available models and pick the right one
available_models = [m.name for m in genai.list_models()]
print("Available Models:", available_models)


class AIRequest():
    """
    Schnittstelle zur Google Gemini AI für game creation
    """
    def __init__(self):
        try:
            # use model in "models/"
            self.model = genai.GenerativeModel(
                "models/"+str(ai_config.ai_model),
                generation_config=generation_config
            )
            self.chat = self.model.start_chat()
            print("AI-Model successful initialized")
        except Exception as e:
            print(f"Error initializing AI model: {str(e)}")
            raise

    def metamorphosis(self, data_string):
        """Order the metamorphosis text --> game."""
        prompt = storage.get_prompt_by_title("metamorphosis")
        role = prompt.role
        case_id = storage.find_highest_case_id()
        ai_query = 'f"""'+str(prompt.content)+'"""'
        print(ai_query)
        exit()
        response = self.model.generate_content(ai_query)

        response_text = response.text.strip()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=case_id,
                                    prompt_id=prompt.id,
                                    free_text=response.text,
                                    ai_config_id=AI_CONFIG_COUNT,
                                    conv_metadata=token_counts)
        storage.add_object_to_db_session(conversation)
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
                informing You about your findings. 
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                          + str(response.usage_metadata.cached_content_token_count) + ", " \
                          + str(response.usage_metadata.candidates_token_count) + ", "\
                          + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=clue.case_id,
                                    prompt_id=2,
                                    free_text=response_text,
                                    ai_config_id=AI_CONFIG_COUNT,
                                    conv_metadata=token_counts)
        storage.add_object_to_db_session(conversation)


        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()
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
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=character.case_id,
                                    prompt_id=2,
                                    free_text=response_text,
                                    ai_config_id=AI_CONFIG_COUNT,
                                    conv_metadata=token_counts)
        storage.add_object_to_db_session(conversation)

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
                Your task is to play the role authentically, not to "win" the interrogation.
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=character.case_id,
                                    prompt_id=2,
                                    free_text=response_text,
                                    ai_config_id=AI_CONFIG_COUNT,
                                    conv_metadata=token_counts)
        storage.add_object_to_db_session(conversation)

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
                Your task is to play the role authentically, not to "win" the interrogation.
                If the evidences cover about 50% of the facts, break down and confess.
                """
        response = self.model.generate_content(prompt)
        response_text = response.text.strip()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=character.case_id,
                                    prompt_id=2,
                                    free_text=response_text,
                                    ai_config_id=AI_CONFIG_COUNT,
                                    conv_metadata=token_counts)
        storage.add_object_to_db_session(conversation)

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
                        Details which are part of of the crime story {data_string} and  
                        associated with {clue} and {search_str} are to reveal with restrictions 
                        as visible below:
                        Any item, trail, witness, location or fact mentioned in the crime story but not in {clue} 
                        is an indicator.
                        If there are no indicators give a subtle hint like: 'Nothing special caught your eye',
                        or: 'The witness shrugs, he has no idea.'  
                        Reveal 1-3 indicators of all indicators associated with {clue} and give a subtle hint to search 
                        again if there are leftovers.
                        Answer in plain english. To this answer append the string '#RV#' followed by a list of the revealed 
                        indicators.     
                        """

        response = self.model.generate_content(prompt)
        response_text = response.text.split('#RV#')[0].strip()
        revealed_indicators = response.text.split('#RV#')[1]
        if revealed_indicators:
            clue.clue_details = clue.clue_details + ',' + revealed_indicators
            db.session.commit()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=clue.case_id,
                                    prompt_id=2,
                                    free_text=response_text,
                                    ai_config_id=AI_CONFIG_COUNT,
                                    conv_metadata=token_counts)
        storage.add_object_to_db_session(conversation)

        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()

        return (response_text)
