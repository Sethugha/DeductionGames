from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    description = db.Column(db.String)
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
        return f"Story: {self.title} from {self.author}."


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
    content = db.Column(db.String)

    def __repr__(self):
        return f"Prompt: {self.title}"
