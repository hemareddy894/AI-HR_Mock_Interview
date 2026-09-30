import sys, os

# Override env before any imports
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['AI_PROVIDER'] = 'demo'
os.environ['DEMO_MODE'] = 'true'
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_USER'] = 'root'
os.environ['DB_PASSWORD'] = ''
os.environ['DB_NAME'] = 'ai_hr_interview'

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Create a minimal test app with SQLite
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TESTING'] = True
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx'}


from models import db
db.init_app(app)

from routes.main_routes import main_bp
from routes.api_routes import api_bp
app.register_blueprint(main_bp)
app.register_blueprint(api_bp) 

with app.app_context():
    db.create_all()
    # Seed roles
    from models import Role
    roles_data = [
        ('Software Developer', 'Build and maintain software applications', 'fas fa-code'),
        ('Web Developer', 'Design and develop web applications', 'fas fa-globe'),
        ('Python Developer', 'Develop applications using Python', 'fab fa-python'),
        ('Data Analyst', 'Analyze data to drive business decisions', 'fas fa-chart-bar'),
        ('HR Executive', 'Manage human resources', 'fas fa-users'),
        ('Other', 'Other professional roles', 'fas fa-star'),
    ]
    for name, desc, icon in roles_data:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name, description=desc, icon=icon))
    db.session.commit()

client = app.test_client()
errors = []

# Protected pages require a student login.
client.post('/login', data={'email': 'test.student@gmail.com'})

def test(label, status, expected=200):
    ok = status == expected
    mark = 'PASS' if ok else 'FAIL'
    print(f"[{mark}] {label}: {status}")
    if not ok:
        errors.append(label)

# Page routes
r = client.get('/')
test('GET /', r.status_code)

r = client.get('/login')
test('GET /login (already logged in -> redirect)', r.status_code, 302)

r = client.get('/select-role')
test('GET /select-role', r.status_code)

r = client.get('/upload-resume')
test('GET /upload-resume (no role -> redirect)', r.status_code, 302)

r = client.get('/history')
test('GET /history', r.status_code)

# API routes
r = client.get('/api/demo-status')
test('GET /api/demo-status', r.status_code)
print('   demo-status response:', r.get_json())

r = client.post('/api/select-role', json={'role_id': 1})
test('POST /api/select-role', r.status_code)
print('   select-role response:', r.get_json())

r = client.post('/api/select-role', json={'role_id': 999})
test('POST /api/select-role (invalid)', r.status_code, 400)

r = client.post('/api/upload-resume')
test('POST /api/upload-resume (no file)', r.status_code, 400)

r = client.post('/api/analyze-resume')
test('POST /api/analyze-resume (no resume)', r.status_code, 400)

r = client.post('/api/start-interview', json={})
test('POST /api/start-interview (no session)', r.status_code, 400)

r = client.post('/api/next-question')
test('POST /api/next-question (no interview)', r.status_code, 400)

r = client.post('/api/submit-answer', json={})
test('POST /api/submit-answer (no question_id)', r.status_code, 400)

r = client.post('/api/complete-interview')
test('POST /api/complete-interview (no interview)', r.status_code, 400)

print()
if errors:
    print(f'FAILED: {len(errors)} test(s) failed: {errors}')
    sys.exit(1)
else:
    print('All tests passed!')
