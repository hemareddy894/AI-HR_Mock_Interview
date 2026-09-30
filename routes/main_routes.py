import re
import uuid
from flask import Blueprint, render_template, request, session, redirect, url_for
from models import db, Interview, Report, Role, CandidateProfile, User
import json

main_bp = Blueprint('main', __name__)

def login_required(view):
    def wrapped_view(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('main.login', next=request.path))
        return view(*args, **kwargs)
    wrapped_view.__name__ = view.__name__
    return wrapped_view

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('main.select_role'))

    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if not re.fullmatch(r'[a-z0-9._%+-]+@gmail\.com', email):
            error = 'Please enter a valid Gmail address.'
        else:
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(email=email, session_id=str(uuid.uuid4()))
                db.session.add(user)
                db.session.commit()
            session.permanent = True
            session['user_id'] = user.id
            session['session_id'] = user.session_id
            next_url = request.args.get('next') or url_for('main.select_role')
            return redirect(next_url if next_url.startswith('/') else url_for('main.select_role'))

    return render_template('login.html', error=error)

@main_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))

@main_bp.route('/')
def index():
    if not session.get('user_id'):
        return render_template('login.html', error=None)
    return render_template('index.html')

@main_bp.route('/select-role')
@login_required
def select_role():
    roles = Role.query.all()
    return render_template('select_role.html', roles=roles)

@main_bp.route('/upload-resume')
@login_required
def upload_resume():
    if 'selected_role' not in session:
        return redirect(url_for('main.select_role'))
    return render_template('upload_resume.html',
                           role_name=session.get('selected_role_name', ''))

@main_bp.route('/analyzing')
@login_required
def analyzing():
    if 'resume_id' not in session:
        return redirect(url_for('main.upload_resume'))
    return render_template('analyzing.html')

@main_bp.route('/interview-setup')
@login_required
def interview_setup():
    if 'profile_id' not in session:
        return redirect(url_for('main.upload_resume'))
    profile_id = session.get('profile_id')
    profile = db.session.get(CandidateProfile, profile_id)
    profile_data = json.loads(profile.profile_json) if profile and profile.profile_json else {}
    return render_template('interview_setup.html',
                           role_name=session.get('selected_role_name', ''),
                           profile=profile_data)

@main_bp.route('/interview')
@login_required
def interview():
    if 'interview_id' not in session:
        return redirect(url_for('main.interview_setup'))
    return render_template('interview.html',
                           interview_id=session.get('interview_id'),
                           role_name=session.get('selected_role_name', ''))

@main_bp.route('/report/<int:interview_id>')
@login_required
def report(interview_id):
    interview = db.session.get(Interview, interview_id)
    if not interview:
        return redirect(url_for('main.index'))
    rpt = Report.query.filter_by(interview_id=interview_id).first()
    if not rpt:
        return redirect(url_for('main.interview'))

    profile_data = {}
    if interview.profile_id:
        cp = db.session.get(CandidateProfile, interview.profile_id)
        if cp and cp.profile_json:
            profile_data = json.loads(cp.profile_json)

    role_name = session.get('selected_role_name', '')
    if interview.role_id:
        role = db.session.get(Role, interview.role_id)
        if role:
            role_name = role.name

    report_data = json.loads(rpt.report_json) if rpt.report_json else {}
    strengths = json.loads(rpt.strengths) if rpt.strengths else []
    improvements = json.loads(rpt.improvements) if rpt.improvements else []
    improvement_plan = json.loads(rpt.improvement_plan) if rpt.improvement_plan else []
    weak_areas = json.loads(rpt.weak_areas) if rpt.weak_areas else []

    # Build question-wise feedback
    qa_feedback = []
    for q in sorted(interview.questions, key=lambda x: x.question_number or 0):
        item = {
            'question': q.question_text,
            'reason': q.question_reason or '',
            'category': q.category or '',
            'answer': '',
            'duration': 0,
            'filler_words': {},
            'score': 0,
            'eval': {}
        }
        if q.answer:
            item['answer'] = q.answer.answer_text or ''
            item['duration'] = q.answer.duration_seconds or 0
            item['filler_words'] = json.loads(q.answer.filler_words) if q.answer.filler_words else {}
            if q.answer.evaluation:
                ev = q.answer.evaluation
                item['score'] = ev.overall_score or 0
                item['eval'] = json.loads(ev.eval_json) if ev.eval_json else {}
        qa_feedback.append(item)

    # Compute interview duration
    if interview.completed_at and interview.started_at:
        duration_secs = (interview.completed_at - interview.started_at).seconds
        interview_duration = duration_secs // 60
    else:
        interview_duration = '—'

    # Compute avg words per answer
    answered_items = [i for i in qa_feedback if i.get('answer')]
    if answered_items:
        total_words = sum(len(i['answer'].split()) for i in answered_items)
        avg_words = round(total_words / len(answered_items))
    else:
        avg_words = 0

    return render_template('report.html',
                           interview=interview,
                           report=rpt,
                           report_data=report_data,
                           profile=profile_data,
                           role_name=role_name,
                           strengths=strengths,
                           improvements=improvements,
                           improvement_plan=improvement_plan,
                           weak_areas=weak_areas,
                           qa_feedback=qa_feedback,
                           avg_words=avg_words,
                           interview_duration=interview_duration)

@main_bp.route('/history')
@login_required
def history():
    user_id = session.get('user_id')
    # Fallback: look up by session_id
    if not user_id and session.get('session_id'):
        from models import User
        u = User.query.filter_by(session_id=session['session_id']).first()
        if u:
            user_id = u.id
    interviews = []
    if user_id:
        interviews = Interview.query.filter_by(user_id=user_id, status='completed')\
                                    .order_by(Interview.completed_at.desc()).all()
    return render_template('history.html', interviews=interviews)

@main_bp.route('/practice-weak-areas/<int:interview_id>')
@login_required
def practice_weak_areas(interview_id):
    interview = db.session.get(Interview, interview_id)
    if not interview:
        return redirect(url_for('main.history'))
    rpt = Report.query.filter_by(interview_id=interview_id).first()
    weak_areas = json.loads(rpt.weak_areas) if rpt and rpt.weak_areas else []
    return render_template('practice.html',
                           interview_id=interview_id,
                           weak_areas=weak_areas,
                           role_name=session.get('selected_role_name', ''))
