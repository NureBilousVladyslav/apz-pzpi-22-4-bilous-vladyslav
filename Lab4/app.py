from config import Config
from flask import Flask
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
from flask_cors import CORS
from db import db

login_manager = LoginManager()
oauth = OAuth()
mail = Mail()
app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
login_manager.init_app(app)
oauth.init_app(app)
mail.init_app(app)

from models import User, Vehicle, Tire, Notification, AlertType, PressureReading, Role

# Create schema, tables, and seed data
with app.app_context():
    try:
        # Create schema
        db.session.execute(db.text('CREATE SCHEMA IF NOT EXISTS tire_pressure'))
        db.session.commit()

        # Create tables
        db.create_all()

        # Seed data
        from db import seed_data
        seed_data(app.config['FORCE_DB_RESET'])

    except Exception as e:
        db.session.rollback()
        print(f"Error initializing database: {str(e)}")
        raise

# Importing routes
from routes import *
app.register_blueprint(auth_bp)
app.register_blueprint(user_profile_bp)
app.register_blueprint(tire_bp)
app.register_blueprint(vehicle_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(iot_bp, url_prefix='/iot')

if __name__ == '__main__':
    app.run()