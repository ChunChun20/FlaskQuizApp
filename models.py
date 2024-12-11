from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import json

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(20), nullable=False)
    difficulty = db.Column(db.String(10), nullable=False)
    question_text = db.Column(db.Text, nullable=False, unique=True)
    correct_answer = db.Column(db.String(20), nullable=False)
    wrong_answers = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Question {self.id} - {self.category}>"

    def set_wrong_answers(self,answers):
        """ Set the wrong answers field"""
        self.wrong_answers = json.dumps(answers)

    def get_wrong_answers(self):
        """Return the wrong answers """
        return json.loads(self.wrong_answers)

class Score(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    score = db.Column(db.Integer,nullable=False)
    category = db.Column(db.String(20),nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime,nullable=False)

    user = db.relationship("User",backref=db.backref('scores',lazy=True))