
"""
ai_request.py - Interface to Google Gemini AI
"""
import os
import json
import time
from dotenv import load_dotenv
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import storage
from data_models import db, AIConfig, Conversation

# Load environment vars
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
# Configurate Google AI
with open('ai_config.json', 'r') as jf:
    ai_config = json.load(jf)
CURRENT_AI_CONFIG = ai_config['config_id']
ZERO = ai_config['zero']
genai.configure(api_key=API_KEY)

# List available models and pick the right one
#available_models = [m.name for m in genai.list_models()]
#print("Available Models:", available_models)
generation_config = GenerationConfig(
    temperature=ai_config['ai_temperature'],
    top_p=ai_config['ai_top_p'],
    top_k=ai_config['ai_top_k'],
    max_output_tokens=ai_config['ai_max_out']
)

class AIRequest():
    """
    Schnittstelle zur Google Gemini AI für game creation
    """
    def __init__(self):
        try:
            # use model in "models/"
            self.model = genai.GenerativeModel(
                ai_config['ai_model'],
                generation_config=generation_config
            )
            self.chat = self.model.start_chat()
            print("AI-Model successful initialized")
        except Exception as e:
            print(f"Error initializing AI model: {str(e)}")
            raise

    def metamorphosis(self, data_string, case_id):
        """Order the metamorphosis text --> game. Uses meta prompting"""
        print("airequest.py - ZERO: ", ZERO)
        if not ZERO:
            prompt = f"""You are a script author ordered to create a script for a deduction game
                         out of the given crime story {data_string}.
                         Your complete knowledge about events, evidences and facts arises from the crime story itself.
                         You must not use any knowledge not included in the story.
                         You must not make own deductions.
                         Do not give explanations, only create a json object as visible below:
                         'title': extracted story title or a telling case title. 
                         'introduction': Short description of the crime case (about 5-7 sentences).
                         'characters': Extract the persons contained in {data_string} and deliver a list of dicts,
                         each containing the full name using key 'name' and the person´s role in the story using key 'role'.
                         'clues': Up to 7 dictionaries each representing a clue with rules as follow:
                         Every item, occurrence or witness linked to the crime is a clue. 
                         Store clues as visible below: 
                         'clue_name': name.
                         'clue_description': A brief description of the clue and its possible connection o the crime.
                         'clue_details': 3 significant attributes pointing to the crime as comma separated strings.
                         Solution:
                         Store the solution as dictionary with keys below:
                         'culprit': The perpetrator´s full name and a telling overview of the mystery.
                         'method': The method how the crime was done matching the story as exactly as possible.
                         'evidence': The clue names which are pointing to the crime, as comma separated strings.
                      """
        else:
            with open('Sources/basic_prompts/prompt1.json') as jf:
                prompt1 = json.load(jf)

            prompt = f"{prompt1['content']}"
        start = time.perf_counter()
        response = self.model.generate_content(prompt)
        elapsed = time.perf_counter() - start
        with open('ai_config.json', 'r') as jf:
            ai_config = json.load(jf)
        current_config = ai_config['config_id']
        statistics = f"statistics/response_candidates{time.strftime("%Y%m%d-%H%M%S")}.log"
        with open(statistics,'w') as sf:
            sf.write(f"prompt: {ai_config['zero']} | {str(response.candidates)}")

        response_text = response.text.strip()

        token_counts = f"""prompt: {response.usage_metadata.prompt_token_count}, 
                           cached: {response.usage_metadata.cached_content_token_count},
                           candidates: {response.usage_metadata.candidates_token_count},
                           total: {response.usage_metadata.total_token_count}
                       """


        conversation = Conversation(case_id=case_id,
                                    prompt_id=1,
                                    free_text=response_text,
                                    ai_config_id=current_config,
                                    conv_metadata=token_counts,
                                    avg_time=elapsed)

        storage.add_object_to_db_session(conversation)
        # Remove Markdown-Code-Block-Format
        response_text = response_text.replace('```json', '').replace('```', '').strip()

        # Validiere und verarbeite die Antwort
        try:
            result = json.loads(response_text)
            return result
        except Exception as e:
            return f"Response not usable as case: \n{response_text}"


    def ai_hint_request(self, data_string, clue):
        """
        Order information about a clue or suspect.
        """
        print("airequest.py - ZERO: ", ZERO)
        if not ZERO:
            prompt = f"""
                    You are the investigator in the field. You have studied the known facts
                    {clue} but you examine the crime site hoping to find
                    additional details.
                    You must not leave the story frame.
                    You must not use any deductions already mentioned in the story.
                    Every additional examination of a clue reveals up to 2 new details if these
                    are mentioned within {data_string} but not in {clue}.
                    Create an answer in plain english as if it came from an observer
                    reporting your findings. Example: 'Examining the chair you found out that
                    someone must have stood on it.' 
                    """
        else:
            with open('Sources/basic_prompts/prompt2.json') as jf:
                prompt2 = json.load(jf)
            prompt = f"Your data: {data_string}, {clue}. {prompt2['content']}"
            print("raw_prompt: ", prompt)
        start = time.perf_counter()
        response = self.model.generate_content(prompt)
        elapsed = time.perf_counter() - start
        with open('ai_config.json', 'r') as jf:
            ai_config = json.load(jf)
        current_config = ai_config['config_id']
        statistics = f"statistics/response_candidates{time.strftime("%Y%m%d-%H%M%S")}.log"
        with open(statistics, 'w') as sf:
            sf.write(str(response.candidates))
        response_text = response.text.strip()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                          + str(response.usage_metadata.cached_content_token_count) + ", " \
                          + str(response.usage_metadata.candidates_token_count) + ", "\
                          + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=clue.case_id,
                                    prompt_id=2,
                                    free_text=response_text,
                                    ai_config_id=current_config,
                                    conv_metadata=token_counts,
                                    avg_time=elapsed)

        storage.add_object_to_db_session(conversation)


        # Remove Markdown-Code-Block-Format
        # response_text = response_text.replace('```json', '').replace('```', '').strip()
        return response_text


    def ai_character_request(self, data_string, character):
        """
        Order information about a witness or suspect.
        """
        print("airequest.py - ZERO: ", ZERO)
        if not ZERO:
            prompt = f"""
                    You are an actor playing an aquaintance of {character} 
                    from the crime story {data_string}. Your complete knowledge is restricted
                    to events and facts described in this crime story.
                    You must not use any knowledge from outside or draw own conclusions.
                    Answer directly without hedging the questions.
                    Your task is to play the role authentical, not to 'win' the interrogation.
                    Example: 'The bell-rope is a fake? So what! It´s an accessory, nothing else!'
                    """
        else:
            with open('Sources/basic_prompts/prompt3.json') as jf:
                prompt3 = json.load(jf)
            prompt = f"Your data: {data_string}, {character}. {prompt3['content']}"
        start = time.perf_counter()
        response = self.model.generate_content(prompt)
        elapsed = time.perf_counter() - start
        with open('ai_config.json', 'r') as jf:
            ai_config = json.load(jf)
        current_config = ai_config['config_id']
        statistics = f"statistics/response_candidates{time.strftime("%Y%m%d-%H%M%S")}.log"
        with open(statistics, 'w') as sf:
            sf.write(str(response.candidates))
        response_text = response.text.strip()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=character.case_id,
                                    prompt_id=3,
                                    free_text=response_text,
                                    ai_config_id=current_config,
                                    conv_metadata=token_counts,
                                    avg_time=elapsed)
        storage.add_object_to_db_session(conversation)

        # Remove Markdown-Code-Block-Format
        # response_text = response_text.replace('```json', '').replace('```', '').strip()
        # result = json.loads(response_text)

        return response_text


    def ai_interrogation(self, data_string, character, clue, solution):
        """
        Order information about a clue or suspect. Always zero.
        """
        print("airequest.py - ZERO: ", ZERO)
        if not ZERO:
            prompt = f"""
                     You are an actor playing the character {character.name} 
                     from the crime story {data_string}. Your complete knowledge is restricted
                     to events and facts described in this crime story.
                     You must not use any knowledge from outside or draw own conclusions.
                     Your task is to play the role authentically, not to 'win' the interrogation.
                     """
        else:
            with open('Sources/basic_prompts/prompt4.json') as jf:
                prompt4 = json.load(jf)
            prompt = f"Your data: {data_string}, {character}. {prompt4['content']}"
        start = time.perf_counter()
        response = self.model.generate_content(prompt)
        elapsed = time.perf_counter() - start
        with open('ai_config.json', 'r') as jf:
            ai_config = json.load(jf)
        current_config = ai_config['config_id']
        statistics = f"statistics/response_candidates{time.strftime("%Y%m%d-%H%M%S")}.log"
        with open(statistics, 'w') as sf:
            sf.write(str(response.candidates))
        response_text = response.text.strip()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=character.case_id,
                                    prompt_id=4,
                                    free_text=response_text,
                                    ai_config_id=current_config,
                                    conv_metadata=token_counts,
                                    avg_time=elapsed)
        storage.add_object_to_db_session(conversation)
        # Remove Markdown-Code-Block-Format
        # response_text = response_text.replace('```json', '').replace('```', '').strip()
        # result = json.loads(response_text)
        return response_text


    def ai_accusation(self, data_string, character, evidences, solution):
        """
        Accusing a suspect you present the evidences you found.
        The culprit will give up.
        few-shot prompt
        """
        print("airequest.py - ZERO: ", ZERO)
        if not ZERO:
            prompt = f"""
                    You are an actor playing the character {character.name} 
                    from the crime story {data_string}, accused of the crime and 
                    confronted with the evidences {evidences}. Your complete knowledge is restricted
                    to events and facts described in this crime story.
                    You must not use any knowledge from outside or draw own conclusions.
                    Your task is to play the role authentically, not to 'win' the accusation.
                    If the evidences cover about 50% of the facts, break down and confess, 
                    attach the string '##WON' to your answer.
                    If the evidences cover less than about 50% then laugh the investigator down, 
                    attach the string '##LOST' to your answer.
                    """
        else:
            with open('Sources/basic_prompts/prompt5.json') as jf:
                prompt5 = json.load(jf)
            prompt = f"Your data: {data_string}, {character}, {evidences}. {prompt5['content']}"
        start = time.perf_counter()
        response = self.model.generate_content(prompt)
        elapsed = time.perf_counter() - start
        with open('ai_config.json', 'r') as jf:
            ai_config = json.load(jf)
        current_config = ai_config['config_id']
        statistics = f"statistics/response_candidates{time.strftime("%Y%m%d-%H%M%S")}.log"
        with open(statistics, 'w') as sf:
            sf.write(str(response.candidates))
        response_text = response.text.strip()
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=character.case_id,
                                    prompt_id=5,
                                    free_text=response_text,
                                    ai_config_id=current_config,
                                    conv_metadata=token_counts,
                                    avg_time=elapsed)
        storage.add_object_to_db_session(conversation)

        # Remove Markdown-Code-Block-Format
        # response_text = response_text.replace('```json', '').replace('```', '').strip()
        # result = json.loads(response_text)
        return response_text


    def search_indicators(self, data_string, search_str, clue):
        """
        Look for additional indicators at a crime scene.
        Few-shot prompt
        """
        print("airequest.py - ZERO: ", ZERO)
        if not ZERO:
            prompt = f"""
                      You are the investigator, looking for indicators 
                      which could deliver additional information about {clue}.
                      Details which are part of of the crime story {data_string} and  
                      associated with {clue} and {search_str} are to reveal with restrictions 
                      as visible below:
                      Any item, trail, witness, location or fact mentioned in the crime story but not in {clue} 
                      is an indicator. 
                      If there are no indicators give a subtle hint. Examples:'Nothing special caught your eye',
                      'The witness shrugs, he has no idea.'  
                      Reveal max 2 indicators of all indicators associated with {clue} and give a subtle hint to search 
                      again if there are leftovers.
                      Answer in plain english. To this answer append the string '#RV#' followed by a list of the revealed 
                      indicators.     
                      """
        else:
            with open('Sources/basic_prompts/prompt6.json') as jf:
                prompt6 = json.load(jf)
            prompt = f"Your data: {search_string}, {clue}. {prompt6['content']}"
        start = time.perf_counter()
        response = self.model.generate_content(prompt)
        elapsed = time.perf_counter() - start
        response_text = response.text.split('#RV#')[0].strip()
        with open('ai_config.json', 'r') as jf:
            ai_config = json.load(jf)
        current_config = ai_config['config_id']
        statistics = f"statistics/response_candidates{time.strftime("%Y%m%d-%H%M%S")}.log"
        with open(statistics, 'w') as sf:
            sf.write(str(response.candidates))
        try:
            revealed_indicators = response.text.split('#RV#')[1]
        except IndexError:
            revealed_indicators = response.text
        finally:
            if revealed_indicators:
                clue.clue_details = clue.clue_details + ', ' + revealed_indicators
                db.session.commit()

        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=clue.case_id,
                                    prompt_id=6,
                                    free_text=response_text,
                                    ai_config_id=current_config,
                                    conv_metadata=token_counts,
                                    avg_time=elapsed)
        storage.add_object_to_db_session(conversation)
        # Remove Markdown-Code-Block-Format
        # response_text = response_text.replace('```json', '').replace('```', '').strip()
        return response_text


    def sarcasm(self, case_id):
        """A caustic remark for clueless investigators, zero-shot prompt."""
        prompt = f"""Create a pretty caustic remark regarding the investigator´s 
                     qualities an innocent person would give if erroneously accused of a crime"""
        start = time.perf_counter()
        response = self.model.generate_content(prompt)
        elapsed = time.perf_counter() - start
        with open('ai_config.json', 'r') as jf:
            ai_config = json.load(jf)
        current_config = ai_config['config_id']
        statistics = f"statistics/response_candidates{time.strftime("%Y%m%d-%H%M%S")}.log"
        with open(statistics, 'w') as sf:
            sf.write(str(response.candidates))
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=case_id,
                                    prompt_id=7,
                                    free_text=response.text,
                                    ai_config_id=current_config,
                                    conv_metadata=token_counts,
                                    avg_time=elapsed)
        storage.add_object_to_db_session(conversation)
        #response_text = response_text.replace('```json', '').replace('```', '').strip()
        return response.text


    def compliment(self, case_id):
        """A whiney remark from self-pitying culprits, zero-shot prompt."""
        prompt = f"""Create a whiney remark, a convicted criminal would give the investigator."""
        start = time.perf_counter()
        response = self.model.generate_content(prompt)
        elapsed = time.perf_counter() - start
        with open('ai_config.json', 'r') as jf:
            ai_config = json.load(jf)
        current_config = ai_config['config_id']
        statistics = f"statistics/response_candidates{time.strftime("%Y%m%d-%H%M%S")}.log"
        with open(statistics, 'w') as sf:
            sf.write(str(response.candidates))
        token_counts = "" + str(response.usage_metadata.prompt_token_count) + ", " \
                       + str(response.usage_metadata.cached_content_token_count) + ", " \
                       + str(response.usage_metadata.candidates_token_count) + ", " \
                       + str(response.usage_metadata.total_token_count)

        conversation = Conversation(case_id=case_id,
                                    prompt_id=8,
                                    free_text=response.text,
                                    ai_config_id=current_config,
                                    conv_metadata=token_counts,
                                    avg_time=elapsed)
        storage.add_object_to_db_session(conversation)
        # response_text = response_text.replace('```json', '').replace('```', '').strip()
        return response.text
