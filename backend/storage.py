import json
import utilities
import os.path
from data_models import db, Clue, Text, Case, Character
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, PendingRollbackError
import shutil



def find_highest_case_id():
    """sometimes I need the next possible case id
    this function retrieves max(case.id) from db
    """
    highest_id = db.session.query(func.max(Case.id)).scalar()
    if highest_id:
        return int(highest_id) + 1
    return 1


def add_story_to_db(text):
    """
    Function to add a new story to db

    :parameter text: New instance of Text
    :return: message
    """
    try:
        db.session.add(text)
        db.session.commit()
        return f"{text.title} from {text.author} successfully added."
    except IntegrityError:
        db.session.rollback()
        return f"Another story with the same data already present. Insertion aborted."
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return  "operation terminated due to a failed insert or update before,  \
                 waiting for an orderly rollback. Cleared transaction log of pending \
                 transactions"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        db.session.rollback()
        return f"Something went wrong: Exception {e}."


def retrieve_stories():
    """Fishes a list of story contents from db
    """
    try:
        stories = db.session.query(Text).all()
        return stories

    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"Something went wrong reading stories: Exception {e}."


def import_text_as_json(file):
    """Imports json file representing raw story text
    keys: title, author, content
    """
    try:
        with open('file','r') as jsonfile:
            data = json.load(jsonfile)
        text = Text(title=data.title, author=data.author, content=data.content)
        message = add_story_to_db(text)
        return message
    except FileNotFoundError:
        return ("No json file found")
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"Something went wrong reading json file: Exception {e}."


def read_case_from_db(case_id):
    """retrieves an unresolved case from db to continue an old game."""
    try:
        case = (db.session.query(Case).filter(Case.id == case_id) \
                .join(Character) \
                .join(Clue) \
                .first())
        print(case) #debug
        return case
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"Something went wrong reading json file: Exception {e}."


def add_case_to_db(ai_case):
    """ reads json (file or aI response) and inserts the data into db table clues"""


    case = Case(title=ai_case['game_title'], description=ai_case['introduction'], questions='What happened?', solution=ai_case['solution'], status='open', source=2)

    db.session.add(case)
    db.session.commit()
    new_id = db.session.query(Case).filter(Case.title == ai_case['title']).first()

    for character in ai_case['characters']:
        new_character = Character(case_id=new_id, name=character['name'], role=character['role'] + ': ' + character['description'] )
        db.session.add(new_character)
        db.session.commit()

    for clue in ai_case['clues']:
        new_clue = Clue(case_id=new_id, clue_name=clue['name'], clue_details=clue['description'])
        db.session.add(new_clue)
        db.session.commit()

    return "inserted json-data into db"
