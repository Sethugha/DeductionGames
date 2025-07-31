from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    introduction = db.Column(db.String)
    solution = db.Column(db.Integer, db.ForeignKey('solutions.id'))
    status = db.Column(db.String(10))
    source = db.Column(db.Integer, db.ForeignKey('texts.id'))



    def __repr__(self):
        return f"Case (id = {self.id}, description = {self.description}"


class Character(db.Model):
    __tablename__ = 'characters'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    name = db.Column(db.String)
    role = db.Column(db.String)



    def __repr__(self):
        return f"Character (id = {self.id}, name = {self.name}, {self.role}"


    def ___str__(self):
        return f"{self.name}, id {self.id}"


class Clue(db.Model):
    __tablename__ = 'clues'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    clue_name = db.Column(db.String)
    clue_description = db.Column(db.String)
    clue_details = db.Column(db.String)


    def __repr__(self):
        return f"Clue(id = {self.id}, name = {self.clue_name}, desc = {self.clue_description}"


class Text(db.Model):
    __tablename__ = 'texts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    content = db.Column(db.String)


    def __repr__(self):
        return f"Story: {self.title} from {self.author} "


class Solution(db.Model):
    __tablename__ = 'solutions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    culprit = db.Column(db.String)
    method = db.Column(db.String)
    evidence = db.Column(db.String)


    def __repr__(self):
        return f"Solution: {self.culprit} used {self.method}."


class Prompt(db.Model):
    __tablename__ = 'prompts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    role = db.Column(db.String)
    content = db.Column(db.String)

    def __repr__(self):
        return f"Prompt: {self.title}"


class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_id = db.Column(db.Integer, db.ForeignKey('cases.id'))
    prompt_id = db.Column(db.Integer, db.ForeignKey('prompts.id'))
    free_text = db.Column(db.String)
    ai_config_id = db.Column(db.Integer, db.ForeignKey('aiconfigs.id'))
    conv_metadata = db.Column(db.String)
    avg_time = db.Column(db.Float)

    def __repr__(self):
        return f"Conversation: Case: {self.case_id} Prompt: {self.prompt_id}: {self.conv_metadata}"


class AIConfig(db.Model):
    __tablename__ = 'aiconfigs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    status = db.Column(db.Integer)
    free_prompts = db.Column(db.Integer)
    ai_model = db.Column(db.String)
    ai_role = db.Column(db.String)
    ai_temperature = db.Column(db.Float)
    ai_top_p = db.Column(db.Float)
    ai_top_k = db.Column(db.Integer)
    ai_max_out = db.Column(db.Integer)

    def __repr__(self):
        return f"AIConfig: Model: {self.ai_model},temp.: {self.ai_temperature}, Max_Token: {self.ai_max_out}"
