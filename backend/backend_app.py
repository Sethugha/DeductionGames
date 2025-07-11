from flask import Flask,render_template, request, jsonify, redirect, url_for, make_response
from sqlalchemy import desc

import ai_request
from data_models import db, Character, Case, Clue, Text, Solution
from os import path
import config
#import utilities
import storage
import json, csv
from ai_request import AIRequest
import datetime

#store absolute path to database file
DB_PATH=path.abspath(path.join(path.dirname(__file__), path.join('data', 'deduction_games.db')))
#store current date for validations
#CURRENT_DATE=datetime.date.now()


#create Flask instance
app = Flask(__name__)
#configure flask_SQLAlchemy
app.config.from_object('config.DevConfig')

ai_client = AIRequest()

@app.route('/')
def home():
    """ Route to home page with Story-selection and stats."""
    case_infos = db.session.query(Case).all()
    stories = db.session.query(Text).all()
    # Charaktere und Hinweise zu jedem Fall sammeln

    return render_template('home.html', stories=stories, cases=case_infos, message="")


@app.route('/select_case', methods=['POST'])
def pick_case():
    """
    Pick an unresolved case from list to continue a previous game
    :return:
    """
    case_id = request.form.get('case')
    if case_id:
        case = db.session.query(Case).filter_by(id=case_id).first()

        if case:
            characters = db.session.query(Character).filter_by(case_id=case.id).all()
            clues = db.session.query(Clue).filter_by(case_id=case.id).all()
            text = db.session.query(Text).filter_by(id=case.source).first()
            title = getattr(text, 'title', None) or case.title or "Case"
            author = getattr(text, 'author', None) or "Unknown"
            description = case.description
            return render_template(
                'case_details.html',
                case=case,
                title=title,
                author=author,
                characters=characters,
                clues=clues
            )
    return redirect(url_for('home'))





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
    text_id = request.form.get('text_id')
    if not text_id:
        return redirect(url_for('home', message="Please select a Story."))
    text = db.session.query(Text).filter_by(id=text_id).first()
    if not text:
        return redirect(url_for('home', message="Story nicht gefunden."))

    # Erzeuge neuen Fall
    new_case = ai_client.ai_request(text.content)
    # Extract case title and introduction
    new_id = storage.find_highest_case_id()
    case_title = new_case.get('case_title', 'Case'+str(new_id))
    introduction = new_case.get('case_description', None)
    solution = new_case.get('solution', None)
    case = Case(title=case_title, description=introduction, solution=None, status='open', source=text.id)
    db.session.add(case)
    db.session.commit()

    # Extract Characters and write into db
    char_list = new_case.get('characters', None)
    for char in char_list:
        character = Character(case_id=new_id, name=char['name'], role = char['role'])
        db.session.add(character)
        db.session.commit()
    # Extract clues and write into db
    clue_list = new_case.get('clues', None)
    for hint in clue_list:
        clue = Clue(case_id=new_id, clue_name=hint['clue_name'], clue_description=hint['description'], clue_details=hint['details'])
        db.session.add(clue)
        db.session.commit()

    new_solution = new_case.get('solution', None)

    new_culprit = new_solution.get('culprit')
    new_method = new_solution.get('method')
    new_evidence = new_solution.get('evidence')
    solution = Solution(case_id=new_id, culprit=new_solution['culprit'], method=new_solution['method'], evidence=new_solution['evidence'])
    db.session.add(solution)
    db.session.commit()

    return render_template('case_details.html', case=case, characters=char_list, clues=clue_list)


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
        message = storage.add_story_to_db(text)
        return render_template('add_text.html', message=message)
    file = request.form.get('json_file')
    if file:
         message = storage.import_text_as_json(file)
         return render_template('add_text.html', message=message)
    return render_template('add_text.html')


@app.route('/view_hints/<location_id>',methods=['GET'])
def view_hints(location_id):
    """
    Returns all hints found in the location (veiled player version).
    """
    pass


@app.route('/statements/<character_id>', methods=['GET'])
def statements(character_id):
    """
    Character interrogation or notes from earlier questioning which contains
    ai generated hints, obviously obscured
    """
    pass


@app.route('/add_fuel', methods=['GET','POST'])
def add_fuel():
    """
    At this endpoint the AI has not only to generate text but build an internal
    "case logic"
    - Input: Details regarding a character, a location or an event from the novel_elements.
    - Output: Description of a hint, a statement, an assumption about possible motivations
      or an element of the poodle´s core.
    (example: If character A is the assumed killer and has been at location B then there might be a
     lost item from character A or a witness report that A was there. The AI must build up such
     logic chains.)
    """
    pass


if __name__ == "__main__":
    """Check for database file and initialization of backend service"""
    if DB_PATH:
        db.init_app(app)
        with app.app_context():
           db.create_all()
        app.run(host="127.0.0.1", port=5002, debug=True)
    else:
        print("No database accessible. Aborting.")


"""
prompt engineering techniques:
1. Role player prompting for character statements and interrogations
   E.g.: you are Yosemite-Sam from the novel. You are interrogated regarding the 
   annihilation of a rabbit using vast amounts of dynamite. You are known as 
   a dynamite-user and there are witness reports beef between you and the unlucky Bunny.   
   Well, you "lost" indeed several crates of dynamite with activated detonators near
   a rabbit-hole but you would never confess even having visited the town ever, much less 
   having done such an atrocity. You are nervous, becoming more and more furious but you
   claim to be innocent like an angel.

   ok, maybe less complex for the beginning:
   You are {character.name}. You are interrogated to a nightly detonation in town.
   You know the culprit but has no interest of telling anything, because [AI generated motivation].
   Answer to the question: "Where have you been last night and did you notice something irregular?"
   You answer should be vague, maybe partially a lie but nevertheless contain a veiled clue of the truth.
   
- this is essential for generation of dynamic clues with ambiguous meanings.

2. constraint-driven Generation with "Ground truth" (for hints):
   First, define the truth, the solution, the villain internal within the AI. Afterwards 
   instruct the AI to generate clues to this truth, but blurred and hazed.
    e.g: 
    Generate a physic clue for a game of deduction as follows:
    Culprit is {character.name}. The crime took place in {location.name}.
    The clue has to be:
    1. findable at the crime location.
    2. related to {character.name} but not too apparent.
    3. formulated in a manner which requires interpretation and deduction
    4. optionally contain a slight misleading component.  
"""
