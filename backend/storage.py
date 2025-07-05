import json
import utilities
import os.path
from data_models import db, Author, Book
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, PendingRollbackError
import shutil



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
        return f"Something went wrong reading stories: Exception {e}."
