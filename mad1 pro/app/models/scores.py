from app import db
from datetime import datetime


class UserScore(db.Model):
    __tablename__ = 'user_scores'

    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)  # FK to quizzes table
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to Quiz
    quiz = db.relationship('Quiz', backref=db.backref('scores', lazy=True))
