from flask import Flask, render_template
from config import Config
from models import db
from sqlalchemy import inspect, text
from datetime import timedelta
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

    db.init_app(app)

    from routes.main_routes import main_bp
    from routes.api_routes import api_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error.html', code=404,
            message='Page not found.',
            detail='The page you are looking for does not exist.'), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('error.html', code=500,
            message='Something went wrong.',
            detail='An internal server error occurred. Please try again.'), 500

    with app.app_context():
        try:
            db.create_all()
            _ensure_user_email_column()
            _seed_roles()
        except Exception as e:
            print(f"[DB Warning] {e}")

    return app

def _ensure_user_email_column():
    columns = {column['name'] for column in inspect(db.engine).get_columns('users')}
    if 'email' not in columns:
        with db.engine.begin() as connection:
            connection.execute(text('ALTER TABLE users ADD COLUMN email VARCHAR(255)'))

def _seed_roles():
    from models import Role
    roles_data = [
        ('Software Developer', 'Build and maintain software applications', 'fas fa-code'),
        ('Web Developer', 'Design and develop web applications', 'fas fa-globe'),
        ('Python Developer', 'Develop applications using Python', 'fab fa-python'),
        ('Java Developer', 'Build enterprise applications with Java', 'fab fa-java'),
        ('Data Analyst', 'Analyze data to drive business decisions', 'fas fa-chart-bar'),
        ('Business Analyst', 'Bridge business needs and technical solutions', 'fas fa-briefcase'),
        ('HR Executive', 'Manage human resources and talent acquisition', 'fas fa-users'),
        ('Other', 'Other professional roles', 'fas fa-star'),
    ]
    for name, desc, icon in roles_data:
        if not Role.query.filter_by(name=name).first():
            db.session.add(Role(name=name, description=desc, icon=icon))
    db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
