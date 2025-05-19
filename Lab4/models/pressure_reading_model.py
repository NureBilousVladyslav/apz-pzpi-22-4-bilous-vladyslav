from typing import Any
from db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from flask import jsonify, Response
from datetime import datetime, timedelta, timezone
from utils import ErrorHandler, Validator
from services.notification_service import send_alert_type_change_notification

class PressureReading(db.Model):
    __tablename__ = 'pressure_reading'

    reading_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tire_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tire.tire_id', ondelete='CASCADE'), nullable=False)
    pressure_value = db.Column(db.Numeric(5, 2), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    tire = db.relationship('Tire', back_populates='pressure_readings')


    @classmethod
    def add_reading(cls, user_id, data: dict) -> tuple[Response, int]:
        """
        Add a new pressure reading for a tire.

        Args:
             user_id: UUID of the user
             data: {
                'tire_id': UUID of the tire
                'pressure_value': float,
                'pressure_unit': str ('bar', 'psi', 'kPa'),
            }

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            from models import Tire, AlertType, Notification

            # Validate input
            Validator.validate_required_fields(data, ['pressure_value', 'tire_id', 'pressure_unit'])

            tire_id = data['tire_id']
            tire = Tire.query.get(uuid.UUID(tire_id))
            if not tire:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Tire {tire_id} not found",
                    status_code=404
                )

            # Validate pressure value
            pressure_value = Validator.validate_pressure(
                value=data['pressure_value'],
                unit=data['pressure_unit'],
                desired_unit=tire.pressure_unit
            )

            # Calculate deviation from optimal pressure
            optimal_pressure = float(tire.optimal_pressure)
            deviation_ratio = pressure_value / optimal_pressure
            old_alert_type = tire.current_alert_type

            # Get all alert types from database ordered by severity
            alert_types = AlertType.query.order_by(AlertType.severity_level.desc()).all()

            # Determine new alert status based on deviation ranges
            new_alert_type = 'normal'  # default value
            for alert in alert_types:
                if (alert.deviation_min <= deviation_ratio <= alert.deviation_max):
                    new_alert_type = alert.alert_type
                    break

            # Create reading
            reading = cls(
                tire_id=tire.tire_id,
                pressure_value=pressure_value
            )
            db.session.add(reading)

            # Update tire status if changed
            notification = None
            if new_alert_type != old_alert_type:
                tire.current_alert_type = new_alert_type
                db.session.commit()

                send_alert_type_change_notification(user_id, tire, old_alert_type, new_alert_type)

            db.session.commit()

            return jsonify({
                "message": "Pressure reading added successfully",
                "reading_id": str(reading.reading_id),
                "pressure_value": float(reading.pressure_value),
                "created_at": reading.created_at.isoformat()
            }), 201

        except ValueError as ve:
            db.session.rollback()
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to add pressure reading"), 500


    @classmethod
    def get_readings_by_timeframe(cls, tire_id: str, data: dict) -> tuple[Response, int]:
        """
        Get pressure readings for a tire within a specific timeframe.

        Args:
            tire_id: UUID of the tire
            data: {
                'days': int,  # Optional
                Number of days to look back (1 for last day, 7 for last week, None for all)
            }
        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            query = cls.query.filter_by(tire_id=uuid.UUID(tire_id))

            days = data.get('days')
            if days is not None:
                if not isinstance(days, int) or days <= 0:
                    raise ValueError("Days parameter must be a positive integer")

                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                query = query.filter(cls.created_at >= cutoff_date)

            readings = query.order_by(cls.created_at.desc()).all()

            readings_data = [{
                "reading_id": str(r.reading_id),
                "pressure_value": float(r.pressure_value),
                "created_at": r.created_at.isoformat()
            } for r in readings]

            return jsonify({
                "tire_id": tire_id,
                "timeframe": f"last {days} days" if days else "all time",
                "count": len(readings_data),
                "readings": readings_data
            }), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to get pressure readings"), 500


    @classmethod
    def get_latest_reading(cls, tire_id: str) -> Any | None:
        """
        Get the most recent pressure reading for a tire.

        Args:
            tire_id: UUID of the tire

        Returns:
            dict: Latest reading data or None if not found
        """
        try:
            reading = cls.query.filter_by(tire_id=uuid.UUID(tire_id)) \
                .order_by(cls.created_at.desc()) \
                .first()

            if not reading:
                return None

            return reading

        except Exception:
            return None
