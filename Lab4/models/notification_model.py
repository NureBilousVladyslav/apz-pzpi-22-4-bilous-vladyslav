from db import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from utils import ErrorHandler, Validator
from flask import jsonify, Response
from sqlalchemy.sql import func
from typing import List, Optional, Any
from sqlalchemy import desc


class Notification(db.Model):
    __tablename__ = 'notification'

    notification_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tire_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tire.tire_id', ondelete='CASCADE'), nullable=False)
    old_alert_type = db.Column(db.String(50), db.ForeignKey('alert_type.alert_type'))
    new_alert_type = db.Column(db.String(50), db.ForeignKey('alert_type.alert_type'))
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    tire = db.relationship('Tire', back_populates='notifications')
    old_alert = db.relationship(
        'AlertType',
        back_populates='old_alert_notifications',
        foreign_keys=[old_alert_type]
    )
    new_alert = db.relationship(
        'AlertType',
        back_populates='new_alert_notifications',
        foreign_keys=[new_alert_type]
    )


    @classmethod
    def add_notification(
            cls,
            tire_id: str,
            old_alert_type: Optional[str],
            new_alert_type: str,
            title: str,
            body: str
    ) -> tuple[Any, int] | None | Any:
        """
        Add a new notification

        Args:
            tire_id: UUID of the tire
            old_alert_type: Previous alert type (can be None)
            new_alert_type: New alert type
            title: Notification title
            body: Notification content

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            Validator.validate_required_fields(
                {'new_alert_type': new_alert_type, 'title': title, 'body': body},
                ['new_alert_type', 'title', 'body']
            )

            notification = cls(
                tire_id=uuid.UUID(tire_id),
                old_alert_type=old_alert_type,
                new_alert_type=new_alert_type,
                title=title.strip(),
                body=body.strip()
            )

            db.session.add(notification)
            db.session.commit()

        except ValueError as ve:
            db.session.rollback()
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to add notification"), 500

    @classmethod
    def get_user_notifications(cls, user_id: str,limit: str = "10") -> tuple[Response, int]:
        """
        Get notifications for a user

        Args:
            user_id: UUID of the user
            limit: Maximum number of notifications to return (as string)

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            from models import Tire, Vehicle

            Validator.validate_limit(limit)

            notifications = cls.query \
                .join(Tire) \
                .join(Vehicle) \
                .filter(Vehicle.user_id == uuid.UUID(user_id)) \
                .order_by(desc(cls.sent_at)) \
                .limit(limit) \
                .all()

            notifications_data = [{
                "notification_id": str(n.notification_id),
                "tire_id": str(n.tire_id),
                "vehicle_id": str(n.tire.vehicle_id),
                "old_alert_type": n.old_alert_type,
                "new_alert_type": n.new_alert_type,
                "title": n.title,
                "body": n.body,
                "sent_at": n.sent_at.isoformat()
            } for n in notifications]

            return jsonify({"notifications": notifications_data}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to get user notifications"), 500


    @classmethod
    def get_vehicle_notifications(cls, vehicle_id: str,limit: str = "10") -> tuple[Response, int]:
        """
        Get notifications for a vehicle

        Args:
            vehicle_id: UUID of the vehicle
            limit: Maximum number of notifications to return

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            from models import Tire

            Validator.validate_limit(limit)

            notifications = cls.query \
                .join(Tire) \
                .filter(Tire.vehicle_id == uuid.UUID(vehicle_id)) \
                .order_by(desc(cls.sent_at)) \
                .limit(limit) \
                .all()

            notifications_data = [{
                "notification_id": str(n.notification_id),
                "tire_id": str(n.tire_id),
                "old_alert_type": n.old_alert_type,
                "new_alert_type": n.new_alert_type,
                "title": n.title,
                "body": n.body,
                "sent_at": n.sent_at.isoformat()
            } for n in notifications]

            return jsonify({
                "vehicle_id": vehicle_id,
                "count": len(notifications_data),
                "notifications": notifications_data
            }), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to get vehicle notifications"), 500
