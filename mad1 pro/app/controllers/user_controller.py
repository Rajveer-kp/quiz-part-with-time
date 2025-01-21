from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.models.subject import Subject
from app.models.quiz import Quiz, Question
from app.models.scores import UserScore
from app import db
from datetime import datetime


# Define the user blueprint
user_bp = Blueprint('user', __name__, url_prefix='/user')


# User Dashboard
@user_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Display the user dashboard with available subjects and chapters.
    """
    subjects = Subject.query.all()  # Fetch all subjects with their chapters
    return render_template('user/dashboard.html', subjects=subjects)


# Take Quiz Route
@user_bp.route('/take_quiz/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def take_quiz(chapter_id):
    """
    Allow users to take a quiz based on the chapter, with timing functionality.
    """
    # Fetch the quiz associated with the chapter
    quiz = Quiz.query.filter_by(chapter_id=chapter_id).first()

    if not quiz:
        # Redirect with an alert if no quiz exists for the chapter
        flash('No quiz available for this subject.', 'error')
        return redirect(url_for('user.dashboard'))

    # Fetch all questions associated with the quiz
    questions = Question.query.filter_by(quiz_id=quiz.id).all()

    if request.method == 'POST':
        # Evaluate the user's answers
        user_answers = request.form
        correct_answers = 0
        total_questions = len(questions)

        for question in questions:
            user_answer = user_answers.get(f'question_{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                correct_answers += 1

        # Save the score without user reference
        user_score = UserScore(
            quiz_id=quiz.id,
            score=correct_answers,
            total_questions=total_questions,
            date_attempted=datetime.utcnow()
        )
        db.session.add(user_score)
        db.session.commit()

        # Flash the user's score
        flash(f'You scored {correct_answers}/{total_questions}!', 'success')
        return redirect(url_for('user.scores'))

    # Pass the duration (in minutes) to the template
    quiz_duration = int(quiz.duration.split()[0]) if quiz.duration else 10  # Default to 10 minutes if no duration

    return render_template(
        'user/take_quiz.html',
        quiz=quiz,
        questions=questions,
        quiz_duration=quiz_duration,
    )


# Scores Page
@user_bp.route('/scores')
@login_required
def scores():
    """
    Display the scores for quizzes.
    """
    scores = UserScore.query.order_by(UserScore.date_attempted.desc()).all()
    return render_template('user/scores.html', scores=scores)
