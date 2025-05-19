from sqlalchemy import MetaData
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

load_dotenv()

metadata = MetaData(schema="tire_pressure")
db = SQLAlchemy(metadata=metadata)

def seed_data():
    """Seed the database with initial data."""
    from models import Role, User, AlertType
    try:
        # Insert roles
        if not Role.query.first():
            roles = [
                {'role_name': 'customer', 'description': None},
                {'role_name': 'admin', 'description': None}
            ]
            for role_data in roles:
                role = Role(**role_data)
                db.session.add(role)
            db.session.commit()

        # Insert admin user
        if not User.query.filter_by(email=os.getenv('ADMIN_EMAIL')).first():
            admin_role = Role.query.filter_by(role_name='admin').first()
            if admin_role:
                # Use pre-hashed password from SQL or hash ADMIN_PASSWORD from .env
                admin = User(
                    name=os.getenv('ADMIN_NAME', 'admin'),
                    email=os.getenv('ADMIN_EMAIL', 'admin@safehome.com'),
                    email_confirmed=True,
                    role_id=admin_role.role_id
                )
                admin.set_password(os.getenv('ADMIN_PASSWORD'))
                db.session.add(admin)
                db.session.commit()

        # Insert alert types
        if not AlertType.query.first():
            alert_types = [
                {
                    'alert_type': 'normal',
                    'deviation_min': 0.90,
                    'deviation_max': 1.10,
                    'severity_level': 0,
                    'description': 'Pressure is normal (deviation from -10% to +10%)'
                },
                {
                    'alert_type': 'low_pressure_warning',
                    'deviation_min': 0.80,
                    'deviation_max': 0.90,
                    'severity_level': 1,
                    'description': 'Slight decrease in pressure (10–20%)'
                },
                {
                    'alert_type': 'low_pressure_critical',
                    'deviation_min': 0.00,
                    'deviation_max': 0.80,
                    'severity_level': 2,
                    'description': 'Critical decrease in pressure (more than 20%)'
                },
                {
                    'alert_type': 'high_pressure_warning',
                    'deviation_min': 1.10,
                    'deviation_max': 1.20,
                    'severity_level': 1,
                    'description': 'Slight increase in pressure (10–20%)'
                },
                {
                    'alert_type': 'high_pressure_critical',
                    'deviation_min': 1.20,
                    'deviation_max': 10.00,
                    'severity_level': 2,
                    'description': 'Critical increase in pressure (more than 20%)'
                }
            ]
            for alert_data in alert_types:
                alert = AlertType(**alert_data)
                db.session.add(alert)
            db.session.commit()

        print("Database seeded successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding database: {str(e)}")
