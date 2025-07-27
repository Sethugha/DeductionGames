from flask import Flask
import config
from data_models import db, Prompt, Case, AIConfig
from os import path

exit()
app = Flask(__name__)

app.config.from_object('config.DevConfig')
DB_PATH=path.abspath(path.join(path.dirname(__file__), path.join('data', 'deduction_games.db')))
source_path=path.abspath(path.join(path.dirname(__file__), path.join('../Sources', 'basic_prompts')))

if DB_PATH:
    db.init_app(app)
    with app.app_context():
        #db.create_all()
        #app.run(host="127.0.0.1", port=5002, debug=True)
        p_data = [
                 {
                  "f_path": "p1.txt",
                  "name": "metamorphosis",
                  "role": "script author"
                },
                {
                "f_path": "p2.txt",
                "name": "hints",
                "role": "investigator at crime scene"
                },
                {
                "f_path": "p3.txt",
                "name": "character",
                "role": "defined"
                },
                {
                "f_path": "p4.txt",
                "name": "interrogation",
                  "role": "crime investigator"
                 },
                 {
                  "f_path": "p5.txt",
                  "name": "accusation",
                "role": "crime investigator"
                },
                {
                "f_path": "p6.txt",
                "name": "indicators",
                "role": "crime investigator"
                }]

        for p in p_data:
            with open(source_path+'/'+p['f_path'], 'r') as phandler:
                content = phandler.read()
            prompt = Prompt(title=p['name'], role=p['role'], content=content)

            try:
                db.session.add(prompt)
                db.session.commit()
                print("db successfully initialized")
            except Exception as e:
                print(f"Something went wrong: {str(e)}" )

#{'gemini_models': "['models/embedding-gecko-001', 'models/gemini-1.0-pro-vision-latest', 'models/gemini-pro-vision', 'models/gemini-1.5-pro-latest', 'models/gemini-1.5-pro-002', 'models/gemini-1.5-pro', 'models/gemini-1.5-flash-latest', 'models/gemini-1.5-flash', 'models/gemini-1.5-flash-002', 'models/gemini-1.5-flash-8b', 'models/gemini-1.5-flash-8b-001', 'models/gemini-1.5-flash-8b-latest', 'models/gemini-2.5-pro-preview-03-25', 'models/gemini-2.5-flash-preview-05-20', 'models/gemini-2.5-flash', 'models/gemini-2.5-flash-lite-preview-06-17', 'models/gemini-2.5-pro-preview-05-06', 'models/gemini-2.5-pro-preview-06-05', 'models/gemini-2.5-pro', 'models/gemini-2.0-flash-exp', 'models/gemini-2.0-flash', 'models/gemini-2.0-flash-001', 'models/gemini-2.0-flash-lite-001', 'models/gemini-2.0-flash-lite', 'models/gemini-2.0-flash-lite-preview-02-05', 'models/gemini-2.0-flash-lite-preview', 'models/gemini-2.0-pro-exp', 'models/gemini-2.0-pro-exp-02-05', 'models/gemini-exp-1206', 'models/gemini-2.0-flash-thinking-exp-01-21', 'models/gemini-2.0-flash-thinking-exp', 'models/gemini-2.0-flash-thinking-exp-1219', 'models/gemini-2.5-flash-preview-tts', 'models/gemini-2.5-pro-preview-tts', 'models/learnlm-2.0-flash-experimental', 'models/gemma-3-1b-it', 'models/gemma-3-4b-it', 'models/gemma-3-12b-it', 'models/gemma-3-27b-it', 'models/gemma-3n-e4b-it', 'models/gemma-3n-e2b-it', 'models/gemini-2.5-flash-lite', 'models/embedding-001', 'models/text-embedding-004', 'models/gemini-embedding-exp-03-07', 'models/gemini-embedding-exp', 'models/gemini-embedding-001', 'models/aqa', 'models/imagen-3.0-generate-002', 'models/imagen-4.0-generate-preview-06-06', 'models/imagen-4.0-ultra-generate-preview-06-06', 'models/veo-2.0-generate-001', 'models/veo-3.0-generate-preview', 'models/gemini-2.5-flash-preview-native-audio-dialog', 'models/gemini-2.5-flash-exp-native-audio-thinking-dialog', 'models/gemini-2.0-flash-live-001', 'models/gemini-live-2.5-flash-preview', 'models/gemini-2.5-flash-live-preview']"}
