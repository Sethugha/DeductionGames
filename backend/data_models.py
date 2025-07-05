from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class Case(db.Model):
    __tablename__ = 'cases'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String)
    characters = db.Column(db.String)
    clues = db.Column(db.String)
    questions =  db.Column(db.String)
    solution = db.Column(db.String)
    status = db.Column(db.String(10))
    source = db.Column(db.Integer, db.ForeignKey('texts.id')


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
    clue_desc = db.Column(db.String)
    clue_details = db.Column(db.String) [note: 'List of details']

    def __repr__(self):
        return f"Clue(id = {self.id}, type = {self.type}, desc = {self.desc}"


class Text(db.Model):
    __tablename__ = 'texts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String)
    author = db.Column(db.String)
    content = db.Column(db.String)


    def __repr__(self):
        return f"Story: {self.title} from {self.author}."
