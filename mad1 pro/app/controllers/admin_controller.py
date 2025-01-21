from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from app import db
from app.models.user import User
from app.models.subject import Chapter, Subject
from app.models.quiz import Quiz, Question
from datetime import datetime

# Create a Blueprint for admin routes
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Decorator to enforce admin-only access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            return "Access Denied", 403
        return f(*args, **kwargs)
    return decorated_function


# Admin Dashboard
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.filter_by(role='user').all()
    subjects = Subject.query.all()
    quizzes = Quiz.query.all()

    # Optional search functionality for subjects
    search_query = request.args.get('search', '')
    if search_query:
        subjects = Subject.query.filter(Subject.name.ilike(f'%{search_query}%')).all()

    return render_template(
        'admin/dashboard.html',
        users=users,
        subjects=subjects,
        quizzes=quizzes,
        current_user=current_user
    )


# Quiz Management
@admin_bp.route('/quiz')
@login_required
@admin_required
def quiz():
    quizzes = Quiz.query.all()
    chapters = Chapter.query.all()
    return render_template('admin/quiz.html', quizzes=quizzes, chapters=chapters)


# Add Subject
@admin_bp.route('/add_subject', methods=['GET', 'POST'])
@login_required
@admin_required
def add_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        if name:
            subject = Subject(name=name)
            db.session.add(subject)
            db.session.commit()
            flash('Subject added successfully!', 'success')
            return redirect(url_for('admin.dashboard'))
        flash('Subject name is required!', 'error')
    return render_template('admin/add_subject.html')


# Add Chapter
@admin_bp.route('/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_chapter(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        question_count = request.form.get('question_count', 0)

        if title:
            new_chapter = Chapter(
                title=title,
                description=description,
                subject_id=subject_id,
                question_count=question_count
            )
            db.session.add(new_chapter)
            db.session.commit()
            flash('Chapter added successfully!', 'success')
            return redirect(url_for('admin.manage_chapters', subject_id=subject_id))
        flash('Chapter title is required!', 'error')

    return render_template('admin/add_chapter.html', subject=subject)


# Edit Chapter
@admin_bp.route('/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        question_count = request.form.get('question_count')

        if title:
            chapter.title = title
            chapter.description = description
            if question_count is not None:
                chapter.question_count = int(question_count)
            db.session.commit()
            flash('Chapter updated successfully!', 'success')
            return redirect(url_for('admin.manage_chapters', subject_id=chapter.subject_id))
        flash('Chapter title is required!', 'error')

    return render_template('admin/edit_chapter.html', chapter=chapter)


# Delete Chapter
@admin_bp.route('/delete_chapter/<int:chapter_id>', methods=['POST'])
@login_required
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully!', 'success')
    return redirect(url_for('admin.manage_chapters', subject_id=subject_id))


# Manage Chapters
@admin_bp.route('/manage_chapters/<int:subject_id>')
@login_required
@admin_required
def manage_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template('admin/manage_chapters.html', subject=subject, chapters=chapters)


# Add Quiz
@admin_bp.route('/add_quiz', methods=['GET', 'POST'])
@login_required
@admin_required
def add_quiz():
    if request.method == 'POST':
        title = request.form.get('title')
        chapter_id = request.form.get('chapter_id')
        date_str = request.form.get('date')
        duration = request.form.get('duration')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'error')
            return redirect(url_for('admin.add_quiz'))

        if title and chapter_id and date and duration:
            new_quiz = Quiz(
                title=title,
                chapter_id=int(chapter_id),
                date=date,
                duration=duration
            )
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('admin.quiz'))
        flash('All fields are required!', 'error')

    chapters = Chapter.query.all()
    return render_template('admin/add_quiz.html', chapters=chapters)


# Edit Question
@admin_bp.route('/edit_question/<int:question_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        question.title = request.form.get('title')
        question.statement = request.form.get('statement')
        question.correct_option = int(request.form.get('correct_option', 0))
        question.option1 = request.form.get('option1')
        question.option2 = request.form.get('option2')
        question.option3 = request.form.get('option3')
        question.option4 = request.form.get('option4')

        if question.title and question.statement and question.correct_option and question.option1 and question.option2:
            db.session.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('admin.quiz'))
        flash('All fields are required!', 'error')

    return render_template('admin/edit_question.html', question=question)


# Delete Quiz
@admin_bp.route('/delete_quiz/<int:quiz_id>', methods=['POST'])
@login_required
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted successfully!', 'success')
    return redirect(url_for('admin.quiz'))


# Add Question
@admin_bp.route('/add_question/<int:quiz_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def add_question(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if request.method == 'POST':
        title = request.form.get('title')
        statement = request.form.get('statement')
        correct_option = request.form.get('correct_option')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')

        if title and statement and correct_option and option1 and option2:
            question = Question(
                quiz_id=quiz_id,
                title=title,
                statement=statement,
                correct_option=int(correct_option),
                option1=option1,
                option2=option2,
                option3=option3,
                option4=option4
            )
            db.session.add(question)
            db.session.commit()
            flash('Question added successfully!', 'success')
            return redirect(url_for('admin.quiz'))
        flash('All fields are required!', 'error')

    return render_template('admin/add_question.html', quiz=quiz)

@admin_bp.route('/delete_question/<int:question_id>', methods=['POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id  # Store the quiz ID for redirection
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully!', 'success')
    return redirect(url_for('admin.quiz'))

