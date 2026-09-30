from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=True)
    name = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    interviews = db.relationship('Interview', backref='user', lazy=True)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(300))
    icon = db.Column(db.String(50))

class Resume(db.Model):
    __tablename__ = 'resumes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(300), nullable=False)
    raw_text = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'
    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=False)
    name = db.Column(db.String(200))
    education = db.Column(db.Text)
    skills = db.Column(db.Text)
    technical_skills = db.Column(db.Text)
    projects = db.Column(db.Text)
    internships = db.Column(db.Text)
    experience = db.Column(db.Text)
    certifications = db.Column(db.Text)
    achievements = db.Column(db.Text)
    career_objective = db.Column(db.Text)
    profile_json = db.Column(db.Text)  # full JSON blob
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Interview(db.Model):
    __tablename__ = 'interviews'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'))
    profile_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id'))
    mode = db.Column(db.String(50))       # Basic HR, Placement HR, etc.
    difficulty = db.Column(db.String(50)) # Easy, Medium, Hard, Adaptive
    style = db.Column(db.String(50))      # Friendly, Professional, etc.
    total_questions = db.Column(db.Integer, default=8)
    status = db.Column(db.String(20), default='active')  # active, completed
    overall_score = db.Column(db.Float)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    questions = db.relationship('Question', backref='interview', lazy=True)
    report = db.relationship('Report', backref='interview', uselist=False)

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    question_number = db.Column(db.Integer)
    question_text = db.Column(db.Text, nullable=False)
    question_reason = db.Column(db.Text)  # why was this asked
    category = db.Column(db.String(100))  # teamwork, leadership, etc.
    asked_at = db.Column(db.DateTime, default=datetime.utcnow)
    answer = db.relationship('Answer', backref='question', uselist=False)

class Answer(db.Model):
    __tablename__ = 'answers'
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answer_text = db.Column(db.Text)
    duration_seconds = db.Column(db.Float)
    filler_words = db.Column(db.Text)  # JSON list
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    evaluation = db.relationship('Evaluation', backref='answer', uselist=False)

class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    id = db.Column(db.Integer, primary_key=True)
    answer_id = db.Column(db.Integer, db.ForeignKey('answers.id'), nullable=False)
    relevance_score = db.Column(db.Float)
    clarity_score = db.Column(db.Float)
    completeness_score = db.Column(db.Float)
    structure_score = db.Column(db.Float)
    overall_score = db.Column(db.Float)
    star_situation = db.Column(db.String(20))
    star_task = db.Column(db.String(20))
    star_action = db.Column(db.String(20))
    star_result = db.Column(db.String(20))
    strengths = db.Column(db.Text)
    improvements = db.Column(db.Text)
    eval_json = db.Column(db.Text)  # full JSON

class Report(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False)
    overall_score = db.Column(db.Float)
    communication_score = db.Column(db.Float)
    answer_quality_score = db.Column(db.Float)
    relevance_score = db.Column(db.Float)
    clarity_score = db.Column(db.Float)
    structure_score = db.Column(db.Float)
    star_score = db.Column(db.Float)
    hr_readiness_score = db.Column(db.Float)
    strengths = db.Column(db.Text)
    improvements = db.Column(db.Text)
    improvement_plan = db.Column(db.Text)
    weak_areas = db.Column(db.Text)  # JSON list
    report_json = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
