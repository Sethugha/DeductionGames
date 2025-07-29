import json
from data_models import db, Clue, Text, Case, Character, Solution, Prompt, Conversation, AIConfig
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError, PendingRollbackError



def find_highest_case_id():
    """sometimes I need the next possible case id
    this function retrieves max(case.id) from db
    """
    highest_id = db.session.query(func.max(Case.id)).scalar()
    if highest_id:
        return int(highest_id) + 1
    return 1


def find_highest_object_id(entity):
    """sometimes I need the next possible id of a table.
    this function retrieves max(id) from entity_table
    """
    highest_id = db.session.query(func.max(entity.id)).scalar()
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


def retrieve_entity_from_db(entity):
    """Retrieves the contents of a given entity (class)
    :parameter entity: The accessed class from the data model
    :return: The contents of a single table
    """
    try:
        data = db.session.query(entity).all()
        return data
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return  "operation terminated due to a failed insert or update before,  \
                 waiting for an orderly rollback. Cleared transaction log of pending \
                 transactions"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"Something went wrong reading stories: Exception {e}."


def retrieve_aiconfig_by_status():
    """Retrieves the active (status == 1) ai configuration"""
    try:
        config = db.session.query(AIConfig).filter(AIConfig.status == 1).first()
        return config
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return  "operation terminated due to a failed insert or update before,  \
                 waiting for an orderly rollback. Cleared transaction log of pending \
                 transactions"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"Something went wrong reading stories: Exception {e}."


def add_object_to_db_session(object):
    """adds a given object to its corresponding class (table)
    :parameter entity: The accessed class from the data model
    :parameter object: the object to add to database
    :return: The contents of a single table
    """
    try:
        message = db.session.add(object)
        db.session.commit()
        return f"{object} added successfully to DB"
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
        return "No json file found"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"Something went wrong reading json file: Exception {e}."


def retrieve_case_via_source_text(source):
    """retrieves a case from db using the source-column.
    if any source (id) matches text_id then the text is already used.
    :param source_id: Addresses source-column all cases
    :return: case object
    """
    if isinstance(source, str) and source.isdigit():
        source = int(source)
    if isinstance(source, int):
        try:
            case = db.session.query(Case.source).filter_by(source=source).first()
            if case:
                return True
            return False
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"Database access failed: {e}."
    return "Error! Invalid Source."



def read_entity_by_id(entity, id):
    """retrieves an unresolved 'entity' from db to continue an old game.
    :param id: The Id of the desired entity object
    :return: entity object
    """
    if entity not in [Case, Character, Clue, Prompt, Solution, Text]:
        return f"Invalid entity {entity}"
    if isinstance(id, str) and id.isdigit():
        id = int(id)
    if isinstance(id, int):
        try:
            data = db.session.query(entity).filter(entity.id == id).first()
            return data
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."
    return f"Error! Invalid {entity}.id Id"


def read_characters_of_single_case(case_id):
    """retrieves characters assigned to a single case.
    :param case_id: The Id of the corresponding case
    :return: characters object list"""
    if isinstance(case_id, str) and case_id.isdigit():
        case_id = int(case_id)
    if isinstance(case_id, int):
        try:
            characters = db.session.query(Character).filter_by(case_id=case_id).all()
            return characters
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."
    return "Error! Invalid Case Id"


def read_clues_of_single_case(case_id):
    """retrieves clues assigned to a single case.
    :param case_id: The Id of the corresponding case
    :return: clues object list
    """
    if isinstance(case_id, str) and case_id.isdigit():
        case_id = int(case_id)
    if isinstance(case_id, int):
        try:
            clues = db.session.query(Clue).filter_by(case_id=case_id).all()
            return clues
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."
    return "Error! Invalid Case Id"


def retrieve_text_for_single_case(id):
    """Using the source (id) of the given case, the source text ist retrieved from db.
    :param id: The column 'source' from cases or a given text.id
    :return: text object
    """
    if isinstance(id, str) and id.isdigit():
        id = int(id)
    if isinstance(id, int):
        try:
            text = db.session.query(Text).filter_by(id=id).first()
            return text
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."
    return "Error! Invalid Id"


def retrieve_clue_from_id(id):
    """given a clue_id the complete corresponding row is retrieved.
    :parameter id: Clue Id
    :return: clue object
    """
    if isinstance(id, str) and id.isdigit():
        id = int(id)
    if isinstance(id, int):
        try:
            clue = db.session.query(Clue).filter_by(id=id).first()
            return clue
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."
    return "Error! Invalid Id"


def retrieve_character_by_id(id):
    """given a clue_id the complete corresponding row is retrieved.
    :parameter id: Clue Id
    :return: clue object
    """
    if isinstance(id, str) and id.isdigit():
        id = int(id)
    if isinstance(id, int):
        try:
            character = db.session.query(Character).filter_by(id=id).first()
            return character
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."
    return "Error! Invalid Id"


def change_case_status(id, status):
    """
    Changes the status of a given case
    :param id: Case Id
    :param status: Case status (open, active or solved)
    :return: success message
    """
    if isinstance(id, str) and id.isdigit():
        id = int(id)
    if isinstance(id, int):
        if status not in ['open', 'active', 'closed']:
            status = 'open'
        try:
            case = db.session.query(Case).filter(Case.id == id).first()
            case.status = status
            db.session.commit()
            return "Successfully updated case-status"
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."
    return "Error! Invalid Id"


def retrieve_case_by_status(status):
    """find a case with status 'status' and return its id"""
    if status.lower() not in ['active', 'open', 'solved']:
        status = 'active'
    try:
        case = db.session.query(Case).filter(Case.status == status).first()
        if case:
            return case
        return None
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return  "operation terminated due to a failed insert or update before,  \
                 waiting for an orderly rollback. Cleared transaction log of pending \
                 transactions"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"DB Access failed: Exception {e}."


def retrieve_solution_by_case_id(id):
    """Retrieve the case´s solution"""
    if isinstance(id, str) and id.isdigit():
        id = int(id)
    if isinstance(id, int):
        try:
            solution = db.session.query(Solution).filter(Solution.case_id == id).first()
            if solution:
                return solution
            return None
        except PendingRollbackError:
            while db.session.registry().in_transaction():
                db.session.rollback()
            return "operation terminated due to a failed insert or update before,  \
                     waiting for an orderly rollback. Cleared transaction log of pending \
                     transactions"
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."


def delete_object_from_db(object):
    """Deletes the given object from db"""
    try:
        db.session.delete(object)
        db.session.commit()
        return f"{object.title} deleted."
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return "operation terminated due to a failed insert or update before,  \
                waiting for an orderly rollback. Cleared transaction log of pending \
                transactions"
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"DB Access failed: Exception {e}."


def deactivate_status(entity):
    """deactivates all status values"""
    try:
        configs = db.session.query(AIConfig).all()
        for config in configs:
            if config.status:
                config.status = 0
        db.session.commit()
        return None
    except PendingRollbackError:
        while db.session.registry().in_transaction():
            db.session.rollback()
        return None
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return None

def json_dump_config(id):
    """dumps active ai_config into json file"""
    ai_config = db.session.query(AIConfig).filter(AIConfig.id==id).first()
    aiconfig = {
                'config_id': id,
                'ai_model': ai_config.ai_model,
                'ai_role': ai_config.ai_role,
                'ai_temperature': ai_config.ai_temperature,
                'ai_top_p': ai_config.ai_top_p,
                'ai_top_k': ai_config.ai_top_k,
                'ai_max_out': ai_config.ai_max_out
                }
    with open('ai_config.json', 'w') as jf:
        json.dump(aiconfig, jf, indent=4)
        return None


def get_prompt_by_title(title):
    try:
        prompt = db.session.query(Prompt).filter(Prompt.title==title).first()
        return prompt
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return None


def gather_conversations(id):
    """Gather conversations by case_id"""
    if isinstance(id, str) and id.isdigit():
        id = int(id)
    if isinstance(id, int):
        try:
            data = db.session.query(Conversation) \
                   .filter(Conversation.case_id==id).all()
            return data
        except Exception as e:  # For Debugging and Testing catch all Exceptions
            return f"DB Access failed: Exception {e}."

def gather_ai_configs():
    """Gather ai configurations by prompt_id"""
    try:
        data = db.session.query(AIConfig).all()
        return data
    except Exception as e:  # For Debugging and Testing catch all Exceptions
        return f"DB Access failed: Exception {e}."
