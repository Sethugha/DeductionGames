from flask import Flask,render_template, request
from data_models import db, Character, Case, Clue, Text, Solution
from os import path
import config
#import utilities
import storage
from ai_request import AIRequest

#store absolute path to database file
DB_PATH=path.abspath(path.join(path.dirname(__file__), path.join('data', 'deduction_games_old.db')))

#create Flask instance
app = Flask(__name__)
#configure flask_SQLAlchemy
app.config.from_object('config.DevConfig')

ai_client = AIRequest()

@app.route('/')
def home():
    """ Route to home page with Story-selection and stats."""
    cases = storage.retrieve_entity_from_db(Case)
    stories = storage.retrieve_entity_from_db(Text)
    return render_template('home.html', stories=stories, cases=cases, message="")


@app.route('/select_case', methods=['GET','POST'])
def select_case():
    """
    Pick an unresolved case from list to continue a previous game
    :return:
    """
    if request.method == 'POST':
        case_id = request.form.get('case_id')
        if case_id:
            cases = storage.retrieve_entity_from_db(Case)
            for case in cases:
                storage.change_case_status(case.id, 'open')
            storage.change_case_status(case_id, 'active')
            case = storage.read_entity_by_id(Case, case_id)
            if case:
                characters = storage.read_characters_of_single_case(case.id)
                clues = storage.read_clues_of_single_case(case.id)
                text = storage.read_entity_by_id(Text, case.source)
                title = getattr(text, 'title', None) or case.title or "Case"
                return render_template(
                                    'card_boxes.html',
                                    case=case,
                                    title=title,
                                    characters=characters,
                                    clues=clues
                                    )

    case = storage.retrieve_case_by_status('active')
    characters = storage.read_characters_of_single_case(case.id)
    clues = storage.read_clues_of_single_case(case.id)
    title = case.title
    return render_template(
         'card_boxes.html',
                           case=case,
                           title=title,
                           characters=characters,
                           clues=clues
                          )



@app.route('/generate_case',methods=['GET','POST'])
def generate_case():
    """
    Based on the extracted novel-parts the AI generates a specific mystery
    and the associated hint-chains. This is the worst part. the AI has to:
    - define a core mystery or crime (the poodle´s core)
    - identify a culprit or a solution and create an appropriate motivation.
    - generate hint chains, some real and relevant, others being red herrings or
      fakes. These hint chains must be linked to characters and/or locations
    - create descriptions of the hints being obfuscated in a manner that they
      can be interpreted in several ways.
    (flow: chapter selection -> flask POST -> AI-model for logic and text generation
     -> flask -> db)
    """
    stories = storage.retrieve_entity_from_db(Text)
    cases = storage.retrieve_entity_from_db(Case)
    text_id = request.form.get('text_id')
    if not text_id:
        return render_template('home.html',
                               stories=stories,
                               cases=cases,
                               message="Please select a Story to convert.")
    text = storage.read_entity_by_id(Text, text_id)
    if not text:
        return render_template('home.html',
                               stories=stories,
                               cases=cases,
                               message="No matching story found in database.")
    # ----------------------------------------------------------------------------------------------
    # Check if text is already used
    # ----------------------------------------------------------------------------------------------
    already_used = True
    already_used = storage.retrieve_case_via_source_text(text_id)
    if already_used:
        return render_template('home.html',
                               stories=stories,
                               cases=cases,
                               message="This story has already been used!")
    # ----------------------------------------------------------------------------------------------
    # Create new case from text.
    # ----------------------------------------------------------------------------------------------
    new_case = ai_client.ai_request(text.content)
    # Extract case title and introduction
    new_id = storage.find_highest_case_id()
    case_title = new_case.get('case_title', 'Case'+str(new_id))
    introduction = new_case.get('case_description', None)
    solution = new_case.get('solution', None)
    case = Case(title=case_title, description=introduction, status='open', source=text.id)
    storage.add_object_to_db_session(case)
    # ----------------------------------------------------------------------------------------------
    # Extract Characters and write into db
    # ----------------------------------------------------------------------------------------------
    char_list = new_case.get('characters', None)
    for char in char_list:
        character = Character(case_id=new_id, name=char['name'], role = char['role'])
        storage.add_object_to_db_session(character)
    # ----------------------------------------------------------------------------------------------
    # Extract clues and write into db
    # ----------------------------------------------------------------------------------------------
    clue_list = new_case.get('clues', None)
    for hint in clue_list:
        clue = Clue(case_id=new_id,
                    clue_name=hint['clue_name'],
                    clue_description=hint['description'],
                    clue_details=hint['details']
                   )
        storage.add_object_to_db_session(clue)
    # ----------------------------------------------------------------------------------------------
    # Extract solution and write into db, currently unused.
    # ----------------------------------------------------------------------------------------------
    new_solution = new_case.get('solution', None)
    new_culprit = new_solution.get('culprit')
    new_method = new_solution.get('method')
    new_evidence = new_solution.get('evidence')
    solution = Solution(case_id=new_id,
                        culprit=new_solution['culprit'],
                        method=new_solution['method'],
                        evidence=new_solution['evidence']
                       )
    storage.add_object_to_db_session(solution)
    return render_template('case_details.html',
                           case=case,
                           characters=char_list,
                           clues=clue_list
                          )


@app.route('/add_text', methods=['GET','POST'])
def add_text():
    """Route for adding own texts into db for later processing"""
    if request.method == 'GET':
        return render_template('add_text.html')

    elif request.method == 'POST':
        title = request.form.get('title')
        author= request.form.get('author')
        content = request.form.get('content')

    if title and author and content:
        text = Text(title=title, author=author, content=content)
        message = storage.add_object_to_db_session(text)
        return render_template('add_text.html', message=message)
    file = request.form.get('json_file')
    if file:
         message = storage.import_text_as_json(file)
         return render_template('add_text.html', message=message)
    return render_template('add_text.html')


@app.route('/view_hint/<clue_id>',methods=['GET','POST'])
def view_hint(clue_id):
    """
    Returns further information about a single clue.
    """
    clue = storage.read_entity_by_id(Clue, clue_id)
    case = storage.read_entity_by_id(Case, clue.case_id)
    text = storage.read_entity_by_id(Text, case.source)
    ai_response = ai_client.ai_hint_request(text.content, clue)
    return render_template('hint_detail.html', clue=clue, details=ai_response)


@app.route('/view_character/<character_id>', methods=['GET','POST'])
def view_character(character_id):
    """
    Returns further information about a single character.
    """
    character = storage.read_entity_by_id(Character, character_id)
    case = storage.read_entity_by_id(Case, character.case_id)
    text = storage.read_entity_by_id(Text, case.source)
    clues = storage.read_clues_of_single_case(character.case_id)
    ai_response = ai_client.ai_character_request(text.content, character)
    return render_template('character_detail.html', character=character, details=ai_response, clues=clues)


@app.route('/ask_character', methods=['GET','POST'])
def ask_character():
    """
    Returns further information about a single character.
    """
    char_id = request.form.get('char_id')
    clue_id = request.form.get('pick_clue')
    question = request.form.get('own_question')
    character = storage.read_entity_by_id(Character, char_id)
    clue = storage.read_entity_by_id(Clue, clue_id)
    clues = storage.read_clues_of_single_case(character.case_id)
    case = storage.read_entity_by_id(Case, character.case_id)
    text = storage.read_entity_by_id(Text, case.source)
    solution = storage.read_entity_by_id(Solution, case.solution)
    if question:
        interrogation = ai_client.ai_interrogation(text.content, character, question, solution)
    else:
        interrogation = ai_client.ai_interrogation(text.content, character, clue , solution)
    return render_template('character_detail.html', character=character, interrogation=interrogation,
                           clues=clues)


@app.route('/accuse_character/<id>', methods=['GET','POST'])
def accuse_character(id):
    """At least the culprit should be found and convicted.
    since this is a serious crime, evidences must be presented.
    Evidences are presented to AI.
    """
    character = storage.read_entity_by_id(Character, id)
    case = storage.read_entity_by_id(Case, character.case_id)
    text = storage.read_entity_by_id(Text, case.source)
    if request.method == 'POST':
        evidences = request.form.get('evidences')
        if evidences:
            solution = storage.retrieve_solution_by_case_id(case.id)
            ai_response = ai_client.ai_accusation(text.content, character, evidences, solution)
            print("character: ", character) #debug
            print("evidences: ", evidences)
            print("solution: ", solution)
            return render_template('accusation.html', character=character, evidences=evidences, validation=ai_response)
    return render_template('accusation.html', character=character)


@app.route('/search_indicators', methods=['GET','POST'])
def search_indicators():
    """Search for additional indicators like items or trails
     to get more details"""
    clue_id = request.form.get('clue_id')
    clue = storage.read_entity_by_id(Clue, clue_id)
    case = storage.read_entity_by_id(Case, clue.case_id)
    text = storage.read_entity_by_id(Text, case.source)
    search_str = request.form.get('indicators')
    if search_str:
        indicators = ai_client.search_indicators(text.content, search_str, clue)
        print("New Indicators: ", indicators)
        return render_template('indicators.html', indicators=indicators, clue=clue)
    return render_template('indicators.html', clue=clue)


if __name__ == "__main__":
    """Check for database file and initialization of backend service"""
    if DB_PATH:
        db.init_app(app)
        #with app.app_context():
        #   db.create_all()
        app.run(host="127.0.0.1", port=5002, debug=True)
    else:
        print("No database accessible. Aborting.")
