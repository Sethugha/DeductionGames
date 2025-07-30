from flask import Flask,render_template, request, redirect, url_for
from data_models import db, Character, Case, Clue, Text, Solution, AIConfig, Conversation
from os import path
import storage
import time
from ai_request import AIRequest
from storage import find_highest_object_id

#store absolute path to database file
DB_PATH=path.abspath(path.join(path.dirname(__file__), path.join('data', 'deduction_games.db')))
TRANSLATION_TABLE = {8217: 180, 8220: 39, 8221: 39, 8212: 45, 233: 101}
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
    ai_config = storage.retrieve_aiconfig_by_status()
    return render_template('home.html', stories=stories, cases=cases, aiconfig=ai_config, message="")


@app.route('/select_case', methods=['GET','POST'])
def select_case():
    """
    Pick an unresolved case from list to continue a previous game
    :return:
    """
    if request.method == 'POST':
        case_id = request.form.get('case_id')
        if case_id:
            case = storage.read_entity_by_id(Case,case_id)
            if case.status == 'closed':
                cases = storage.retrieve_entity_from_db(Case)
                stories = storage.retrieve_entity_from_db(Text)
                ai_config = storage.retrieve_aiconfig_by_status()
                return render_template('home.html', stories=stories, cases=cases,
                                       aiconfig=ai_config, message="This case is already solved.")
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
    new_id = storage.find_highest_case_id()
    new_case = ai_client.metamorphosis(text.content, new_id)
    if isinstance(new_case, str):
        cases = storage.retrieve_entity_from_db(Case)
        stories = storage.retrieve_entity_from_db(Text)
        ai_config = storage.retrieve_aiconfig_by_status()
        return render_template('home.html', stories=stories, cases=cases, aiconfig=ai_config,
                               message=new_case)
    # Extract case title and introduction
    case_title = new_case.get('title', 'Case'+str(new_id))
    introduction = new_case.get('introduction', None)
    solution = new_case.get('solution', None)
    case = Case(title=case_title, introduction=introduction, status='open', source=text.id)
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
    print("hint-list")
    for hint in clue_list:
        print(hint)
        clue = Clue(case_id=new_id,
                    clue_name=hint["clue_name"],
                    clue_description=hint["clue_description"],
                    clue_details=hint["clue_details"]
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
        text = request.form.get('content')
        content = text.translate(TRANSLATION_TABLE)
        original_txt = len(content)

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
            response = ai_response.split('##')[0]
            condition = ai_response.split('##')[1]
            if condition == 'LOST':
                condition = None
                remark = ai_client.sarcasm(case.id)
            else:
                remark = ai_client.compliment(case.id)
            case.status = 'closed'
            db.session.commit()

            return render_template('laudatio.html', character=character, validation=response, condition=condition, remark=remark)
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
        #print("New Indicators: ", indicators) # debug
        clue.clue_details += indicators
        db.session.commit()
        return render_template('indicators.html', indicators=indicators, clue=clue)
    return render_template('indicators.html', clue=clue)


@app.route('/config_ai', methods=['POST'])
def config_ai():
    """reads active configuration from db and adjusts the genai-setup"""
    new_id = find_highest_object_id(AIConfig)
    cases = storage.retrieve_entity_from_db(Case)
    stories = storage.retrieve_entity_from_db(Text)
    ai_config = storage.retrieve_aiconfig_by_status()
    changed = request.form.get('changed')
    ai_model = request.form.get('model') or ai_config.ai_model
    ai_role = request.form.get('role') or ai_config.ai_role
    ai_temperature = request.form.get('temp') or ai_config.ai_temperature
    ai_top_p = request.form.get('top_p') or ai_config.ai_top_p
    ai_top_k = request.form.get('top_k') or ai_config.ai_top_k
    ai_max_out = request.form.get('max_out') or ai_config.ai_max_out
    zero = request.form.get('zero_checked')

    if changed:
        new_config = AIConfig(status=1,
                              ai_model=ai_model,
                              ai_role=ai_role,
                              ai_temperature=ai_temperature,
                              ai_top_p=ai_top_p,
                              ai_top_k=ai_top_k,
                              ai_max_out=ai_max_out
                             )
        storage.deactivate_status(AIConfig)
        storage.add_object_to_db_session(new_config)
        storage.json_dump_config(new_id)
        # reinit ai_client
        ai_client = AIRequest()
        message = f"AI reconfigured to profile {new_id}"
    return render_template('home.html', stories=stories, cases=cases, aiconfig=new_config,
                               message=message or "")


@app.route('/del_case', methods=['POST'])
def del_case():
    """deletes selected case from db"""
    case_id = request.form.get('case_id')
    if case_id:
        case = storage.read_entity_by_id(Case, case_id)
        characters = storage.read_characters_of_single_case(case_id)
        clues = storage.read_clues_of_single_case(case_id)
        solution = storage.retrieve_solution_by_case_id(case_id)
        for character in characters:
            storage.delete_object_from_db(character)
        for clue in clues:
            storage.delete_object_from_db(clue)
        storage.delete_object_from_db(solution)
        message = storage.delete_object_from_db(case)
    cases = storage.retrieve_entity_from_db(Case)
    stories = storage.retrieve_entity_from_db(Text)
    ai_config = storage.retrieve_aiconfig_by_status()
    return render_template('home.html', stories=stories, cases=cases, aiconfig=ai_config, message=message)


@app.route('/del_text', methods=['POST'])
def del_text():
    """deletes selected text from db"""
    text_id=request.form.get('text_id')
    if text_id:
        text = storage.read_entity_by_id(Text, text_id)
        message= storage.delete_object_from_db(text)
    cases = storage.retrieve_entity_from_db(Case)
    stories = storage.retrieve_entity_from_db(Text)
    ai_config = storage.retrieve_aiconfig_by_status()
    return render_template('home.html', stories=stories, cases=cases, aiconfig=ai_config, message=message)


@app.route('/analysis', methods=['POST'])
def analysis():
    """Brief comparison of ai-parameters and runtime."""
    case_id = request.form.get('aux_id')
    if case_id:
        conversations = storage.gather_conversations(case_id)
        con_configs = storage.gather_ai_configs()
        if conversations and con_configs:
            analysis = f"statistics/conversations{time.strftime("%Y%m%d-%H%M%S")}.txt"
            with (open(analysis, 'w') as sf):
                for record in conversations:
                    for config in con_configs:
                        if config:
                            if record.ai_config_id == config.id:
                                analist = [str(record.prompt_id),
                                           str(record.ai_config_id),
                                           str(record.conv_metadata),
                                           str(config.ai_temperature),
                                           str(config.ai_top_p),
                                           str(config.ai_top_k),
                                           str(config.ai_max_out),
                                           str(record.avg_time)
                                          ]
                                sf.write(f"{analist}\n")

    return redirect(url_for('home'))


if __name__ == "__main__":
    """Check for database file and initialization of backend service"""
    if DB_PATH:
        db.init_app(app)
        #with app.app_context():
        #    db.create_all()
        app.run(host="127.0.0.1", port=5002, debug=True)
    else:
        print("No database accessible. Aborting.")
