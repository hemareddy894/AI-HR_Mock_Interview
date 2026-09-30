import os
import uuid
import json
from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
from config import Config
from models import db, User, Role, Resume, CandidateProfile, Interview, Question
from services.resume_service import allowed_file, extract_text_from_file
from services.ai_service import (analyze_resume, generate_initial_question,
                                  generate_followup_question, generate_weak_area_questions)
from services.evaluation_service import (save_answer_and_evaluate,
                                          build_final_report, get_conversation_history)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_or_create_user():
    session.permanent = True
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    user = User.query.filter_by(session_id=session['session_id']).first()
    if not user:
        user = User(session_id=session['session_id'])
        db.session.add(user)
        db.session.commit()
    return user

def get_profile():
    profile_id = session.get('profile_id')
    if not profile_id:
        return {}
    cp = db.session.get(CandidateProfile, profile_id)
    if cp and cp.profile_json:
        return json.loads(cp.profile_json)
    return {}

# ── Role ───────────────────────────────────────────────────────────────────────
@api_bp.route('/select-role', methods=['POST'])
def select_role():
    data = request.get_json()
    role_id = data.get('role_id')
    role = db.session.get(Role, role_id)
    if not role:
        return jsonify({'error': 'Invalid role'}), 400
    session['selected_role'] = role_id
    session['selected_role_name'] = role.name
    return jsonify({'success': True, 'role_name': role.name})

# ── Resume Upload ──────────────────────────────────────────────────────────────
@api_bp.route('/upload-resume', methods=['POST'])
def upload_resume():
    if 'selected_role' not in session:
        return jsonify({'error': 'Please select a role first'}), 400

    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['resume']
    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Only PDF, DOC, DOCX files are allowed'}), 400

    # Secure filename
    ext = file.filename.rsplit('.', 1)[1].lower()
    safe_name = f"{uuid.uuid4().hex}.{ext}"
    upload_path = os.path.join(Config.UPLOAD_FOLDER, safe_name)
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(upload_path)

    try:
        resume_text = extract_text_from_file(upload_path)
    except ValueError as e:
        os.remove(upload_path)
        return jsonify({'error': str(e)}), 400

    if not resume_text.strip():
        os.remove(upload_path)
        return jsonify({'error': 'Could not extract text from resume. Please check the file.'}), 400

    user = get_or_create_user()
    resume = Resume(user_id=user.id, filename=safe_name, raw_text=resume_text)
    db.session.add(resume)
    db.session.commit()

    session['resume_id'] = resume.id
    return jsonify({'success': True, 'resume_id': resume.id,
                    'filename': file.filename, 'text_length': len(resume_text)})

# ── Resume Analysis ────────────────────────────────────────────────────────────
@api_bp.route('/analyze-resume', methods=['POST'])
def analyze_resume_route():
    resume_id = session.get('resume_id')
    if not resume_id:
        return jsonify({'error': 'No resume found'}), 400

    resume = db.session.get(Resume, resume_id)
    if not resume:
        return jsonify({'error': 'Resume not found'}), 404

    role_name = session.get('selected_role_name', 'General')

    profile_data = analyze_resume(resume.raw_text, role_name)

    # Save candidate profile
    cp = CandidateProfile(
        resume_id=resume.id,
        name=profile_data.get('name', ''),
        education=profile_data.get('education', ''),
        skills=json.dumps(profile_data.get('skills', [])),
        technical_skills=json.dumps(profile_data.get('technical_skills', [])),
        projects=json.dumps(profile_data.get('projects', [])),
        internships=json.dumps(profile_data.get('internships', [])),
        experience=profile_data.get('experience', ''),
        certifications=json.dumps(profile_data.get('certifications', [])),
        achievements=json.dumps(profile_data.get('achievements', [])),
        career_objective=profile_data.get('career_objective', ''),
        profile_json=json.dumps(profile_data)
    )
    db.session.add(cp)
    db.session.commit()

    session['profile_id'] = cp.id
    if profile_data.get('name'):
        user = get_or_create_user()
        user.name = profile_data['name']
        db.session.commit()

    return jsonify({'success': True, 'profile': profile_data})

# ── Interview Setup ────────────────────────────────────────────────────────────
@api_bp.route('/start-interview', methods=['POST'])
def start_interview():
    data = request.get_json()
    if 'selected_role' not in session or 'profile_id' not in session:
        return jsonify({'error': 'Missing role or profile'}), 400

    user = get_or_create_user()
    length_map = {'short': 5, 'standard': 8, 'long': 12}
    total_q = length_map.get(data.get('length', 'standard'), 8)

    interview = Interview(
        user_id=user.id,
        role_id=session['selected_role'],
        resume_id=session.get('resume_id'),
        profile_id=session.get('profile_id'),
        mode=data.get('mode', 'Placement HR'),
        difficulty=data.get('difficulty', 'Medium'),
        style=data.get('style', 'Professional'),
        total_questions=total_q,
        status='active'
    )
    db.session.add(interview)
    db.session.commit()
    session['interview_id'] = interview.id
    session['user_id'] = user.id
    return jsonify({'success': True, 'interview_id': interview.id})

# ── Get Next Question ──────────────────────────────────────────────────────────
@api_bp.route('/next-question', methods=['POST'])
def next_question():
    interview_id = session.get('interview_id')
    if not interview_id:
        return jsonify({'error': 'No active interview'}), 400

    interview = db.session.get(Interview, interview_id)
    if not interview or interview.status != 'active':
        return jsonify({'error': 'Interview not active'}), 400

    question_number = len(interview.questions)
    if question_number >= interview.total_questions:
        return jsonify({'done': True})

    profile = get_profile()
    role_name = session.get('selected_role_name', 'General')
    history = get_conversation_history(interview_id)

    if question_number == 0:
        q_data = generate_initial_question(
            profile, role_name, interview.mode, interview.difficulty, interview.style
        )
    else:
        q_data = generate_followup_question(
            profile, role_name, interview.mode, interview.difficulty, interview.style,
            history, question_number, interview.total_questions
        )

    question = Question(
        interview_id=interview_id,
        question_number=question_number + 1,
        question_text=q_data['text'],
        question_reason=q_data.get('reason', ''),
        category=q_data.get('category', '')
    )
    db.session.add(question)
    db.session.commit()

    return jsonify({
        'question_id': question.id,
        'question_text': question.question_text,
        'question_reason': question.question_reason or '',
        'question_number': question_number + 1,
        'total_questions': interview.total_questions,
        'done': False
    })

# ── Submit Answer ──────────────────────────────────────────────────────────────
@api_bp.route('/submit-answer', methods=['POST'])
def submit_answer():
    data = request.get_json()
    question_id = data.get('question_id')
    answer_text = data.get('answer_text', '').strip()
    duration = data.get('duration_seconds', 0)

    if not question_id:
        return jsonify({'error': 'Missing question_id'}), 400

    profile = get_profile()
    role_name = session.get('selected_role_name', 'General')

    eval_data = save_answer_and_evaluate(question_id, answer_text, duration, profile, role_name)
    if eval_data is None:
        return jsonify({'error': 'Question not found'}), 404

    return jsonify({'success': True, 'evaluation': eval_data})

# ── Complete Interview ─────────────────────────────────────────────────────────
@api_bp.route('/complete-interview', methods=['POST'])
def complete_interview():
    interview_id = session.get('interview_id')
    if not interview_id:
        return jsonify({'error': 'No active interview'}), 400

    report = build_final_report(interview_id)
    if not report:
        return jsonify({'error': 'Could not generate report'}), 500

    return jsonify({'success': True, 'interview_id': interview_id,
                    'overall_score': report.overall_score})

# ── Weak Area Practice ─────────────────────────────────────────────────────────
@api_bp.route('/weak-area-questions/<int:interview_id>', methods=['GET'])
def weak_area_questions(interview_id):
    from models import Report
    rpt = Report.query.filter_by(interview_id=interview_id).first()
    weak_areas = json.loads(rpt.weak_areas) if rpt and rpt.weak_areas else ['communication', 'STAR structure']

    profile = get_profile()
    role_name = session.get('selected_role_name', 'General')
    questions = generate_weak_area_questions(profile, role_name, weak_areas, count=5)
    return jsonify({'questions': questions, 'weak_areas': weak_areas})

# ── Interview Status ───────────────────────────────────────────────────────────
@api_bp.route('/interview-status', methods=['GET'])
def interview_status():
    interview_id = session.get('interview_id')
    if not interview_id:
        return jsonify({'active': False})
    interview = db.session.get(Interview, interview_id)
    if not interview:
        return jsonify({'active': False})
    return jsonify({
        'active': interview.status == 'active',
        'interview_id': interview_id,
        'questions_asked': len(interview.questions),
        'total_questions': interview.total_questions
    })

# ── Demo Mode Check ────────────────────────────────────────────────────────────
@api_bp.route('/demo-status', methods=['GET'])
def demo_status():
    return jsonify({'demo_mode': Config.DEMO_MODE or Config.AI_PROVIDER == 'demo'})
