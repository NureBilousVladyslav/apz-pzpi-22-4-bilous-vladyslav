from db import db

class AlertType(db.Model):
    __tablename__ = 'alert_type'

    alert_type = db.Column(db.String(50), primary_key=True)
    direction = db.Column(db.String(10))
    deviation_min = db.Column(db.Numeric(5, 2))
    deviation_max = db.Column(db.Numeric(5, 2))
    severity_level = db.Column(db.Integer)
    description = db.Column(db.Text)

    current_alert_tires = db.relationship(
        'Tire',
        back_populates='current_alert',
        foreign_keys='Tire.current_alert_type'
    )
    old_alert_notifications = db.relationship(
        'Notification',
        back_populates='old_alert',
        foreign_keys='Notification.old_alert_type'
    )
    new_alert_notifications = db.relationship(
        'Notification',
        back_populates='new_alert',
        foreign_keys='Notification.new_alert_type'
    )