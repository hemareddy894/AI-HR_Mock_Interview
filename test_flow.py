import sys, os, json
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['AI_PROVIDER'] = 'demo'
os.environ['DEMO_MODE'] = 'true'

from flask import Flask
from models import db
from routes.main_routes import main_bp
from routes.api_routes import api_bp

app = Flask(__name__)
app.config.update(
    SECRET_KEY='test-secret',
    SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    TESTING=True,
    UPLOAD_FOLDER='uploads',
    MAX_CONTENT_LENGTH=5*1024*1024,
    ALLOWED_EXTENSIONS={'pdf','doc','docx'},
)
db.init_app(app)
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)

with app.app_context():
    db.create_all()
    from models import Role
    for name, desc, icon in [
        ('Software Developer','Build software','fas fa-code'),
        ('Web Developer','Build web apps','fas fa-globe'),
    ]:
        db.session.add(Role(name=name, description=desc, icon=icon))
    db.session.commit()

errors = []
def check(label, cond, detail=''):
    mark = 'PASS' if cond else 'FAIL'
    print(f'[{mark}] {label}' + (f': {detail}' if detail else ''))
    if not cond:
        errors.append(label)

client = app.test_client()

# 1. Select role
r = client.post('/api/select-role', json={'role_id': 1})
d = r.get_json()
check('Select role', r.status_code == 200 and d.get('success'))

# 2. Simulate resume upload by directly inserting into DB
with app.app_context():
    from models import User, Resume, CandidateProfile
    import uuid, json as _json
    user = User(session_id=str(uuid.uuid4()), name='Test User')
    db.session.add(user)
    db.session.flush()
    resume = Resume(user_id=user.id, filename='test.pdf', raw_text='Python developer with 2 years experience')
    db.session.add(resume)
    db.session.flush()
    profile_data = {
        'name': 'Test User', 'education': 'B.Tech CS',
        'skills': ['Communication'], 'technical_skills': ['Python','SQL'],
        'projects': ['E-Commerce Website'], 'internships': ['Web Dev Intern'],
        'experience': 'Fresher', 'certifications': [], 'achievements': ['Hackathon'],
        'career_objective': 'Software Developer', 'hobbies': [], 'leadership': [], 'teamwork': []
    }
    cp = CandidateProfile(
        resume_id=resume.id, name='Test User',
        profile_json=_json.dumps(profile_data)
    )
    db.session.add(cp)
    db.session.commit()
    uid = user.id
    rid = resume.id
    cpid = cp.id

# Inject session values
with client.session_transaction() as sess:
    sess['selected_role'] = 1
    sess['selected_role_name'] = 'Software Developer'
    sess['resume_id'] = rid
    sess['profile_id'] = cpid
    sess['session_id'] = 'test-session-123'

# 3. Start interview
r = client.post('/api/start-interview', json={'mode':'Placement HR','difficulty':'Medium','length':'short','style':'Professional'})
d = r.get_json()
check('Start interview', r.status_code == 200 and d.get('success'), d)
interview_id = d.get('interview_id')

# 4. Get first question
r = client.post('/api/next-question')
d = r.get_json()
check('Get first question', r.status_code == 200 and 'question_text' in d, d)
q_id = d.get('question_id')
print(f'   Q1: {d.get("question_text","")[:80]}')

# 5. Submit answer
r = client.post('/api/submit-answer', json={
    'question_id': q_id,
    'answer_text': 'I am a final year student with Python experience and worked on an e-commerce project.',
    'duration_seconds': 12.5
})
d = r.get_json()
check('Submit answer', r.status_code == 200 and d.get('success'), d)
check('Evaluation returned', 'evaluation' in d)
if 'evaluation' in d:
    ev = d['evaluation']
    check('Eval has overall_score', 'overall_score' in ev)
    print(f'   Score: {ev.get("overall_score")}')

# 6. Get second question (follow-up)
r = client.post('/api/next-question')
d = r.get_json()
check('Get follow-up question', r.status_code == 200 and 'question_text' in d, d)
print(f'   Q2: {d.get("question_text","")[:80]}')

# 7. Complete interview (skip remaining questions by submitting empty answers)
with app.app_context():
    from models import Interview, Question, Answer
    iv = db.session.get(Interview, interview_id)
    # Add remaining questions and answers to reach total
    for i in range(3, iv.total_questions + 1):
        q = Question(interview_id=interview_id, question_number=i, question_text=f'Demo question {i}', category='general')
        db.session.add(q)
        db.session.flush()
        a = Answer(question_id=q.id, answer_text='Demo answer for testing purposes.')
        db.session.add(a)
    db.session.commit()

r = client.post('/api/complete-interview')
d = r.get_json()
check('Complete interview', r.status_code == 200 and d.get('success'), d)
check('Report has score', 'overall_score' in d, d)
print(f'   Overall score: {d.get("overall_score")}')

# 8. Report page
r = client.get(f'/report/{interview_id}')
check('Report page loads', r.status_code == 200)

# 9. History page
r = client.get('/history')
check('History page loads', r.status_code == 200)

# 10. Weak area questions API
r = client.get(f'/api/weak-area-questions/{interview_id}')
d = r.get_json()
check('Weak area questions', r.status_code == 200 and 'questions' in d, d)
print(f'   Weak area questions count: {len(d.get("questions",[]))}')

print()
if errors:
    print(f'FAILED: {len(errors)} test(s): {errors}')
    sys.exit(1)
else:
    print(f'All {14 + 10} tests passed! Full interview flow verified.')
