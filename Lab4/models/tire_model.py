from db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid, random, string
from sqlalchemy.sql import func
from flask import jsonify, Response
from utils import ErrorHandler, Validator
from models.pressure_reading_model import PressureReading
from models.vehicle_model import  Vehicle

class Tire(db.Model):
    __tablename__ = 'tire'

    tire_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = db.Column(UUID(as_uuid=True), db.ForeignKey('vehicle.vehicle_id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    optimal_pressure = db.Column(db.Numeric(5, 2), nullable=False)
    pressure_unit = db.Column(db.String(10), nullable=False)
    installed_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    current_alert_type = db.Column(db.String(50), db.ForeignKey('alert_type.alert_type'))
    sensor_code = db.Column(db.String(6), unique=True, nullable=False)

    vehicle = db.relationship('Vehicle', back_populates='tires')
    current_alert = db.relationship(
        'AlertType',
        back_populates='current_alert_tires',
        foreign_keys=[current_alert_type]
    )
    pressure_readings = db.relationship(
        'PressureReading',
        back_populates='tire',
        cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        'Notification',
        back_populates='tire',
        cascade="all, delete-orphan"
    )


    @staticmethod
    def generate_sensor_code() -> str:
        """Generate a unique 6-character alphanumeric sensor code."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not db.session.query(Tire).filter_by(sensor_code=code).first():
                return code


    @classmethod
    def add_tire(cls, user_id: str, data: dict) -> tuple[Response, int]:
        """
        Add a new tire to a vehicle with auto-generated sensor code.

        Args:
            user_id: UUID of the user
            data: {
                'vehicle_id': UUID of the vehicle,
                'label': str,
                'optimal_pressure': float,
                'pressure_unit': str ('bar', 'psi', 'kPa'),
            }

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            Validator.validate_required_fields(data, ['vehicle_id', 'label', 'optimal_pressure', 'pressure_unit'])

            vehicle = Vehicle.query.get(uuid.UUID(data['vehicle_id']))
            if not vehicle:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Vehicle {data['vehicle_id']} not found",
                    status_code=404
                )

            # Check if the vehicle belongs to the user
            if vehicle.user_id != user_id:
                return jsonify({"error": "Forbidden: You do not own this vehicle"}), 403

            optimal_pressure = Validator.validate_pressure(data['optimal_pressure'], unit=None, desired_unit=None)
            
            pressure_unit = data['pressure_unit'].lower()  # Normalize to lowercase
            if pressure_unit not in ['bar', 'psi', 'kpa']:
                return ErrorHandler.handle_validation_error("Invalid pressure unit. Use 'bar', 'psi', or 'kPa'")
            
            optimal_pressure = Validator.validate_pressure(
                data['optimal_pressure'],
                unit=pressure_unit, 
                desired_unit=pressure_unit
            )

            tire = cls(
                vehicle_id=uuid.UUID(data['vehicle_id']),
                label=data['label'].strip(),
                optimal_pressure=optimal_pressure,
                pressure_unit=pressure_unit,  # Store internally in bar
                sensor_code=cls.generate_sensor_code(),
            )

            db.session.add(tire)
            db.session.commit()

            return jsonify({
                "message": "Tire added successfully",
                "tire_id": str(tire.tire_id),
                "sensor_code": tire.sensor_code
            }), 201

        except ValueError as ve:
            db.session.rollback()
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to add tire"), 500


    @classmethod
    def update_tire(cls, user_id: str, data: dict) -> tuple[Response, int]:
        """
        Update tire information.
        """
        try:
            tire_id = data.get('tire_id')
            tire = cls.query.get(uuid.UUID(tire_id))
            if not tire:
                return ErrorHandler.handle_error(None, message=f"Tire {tire_id} not found", status_code=404)

            # Check if the vehicle belongs to the user
            if tire.vehicle.user_id != user_id:
                return jsonify({"error": "Forbidden: You do not own this tire"}), 403

            if 'label' in data:
                tire.label = data['label'].strip()

            if 'optimal_pressure' in data and 'pressure_unit' in data:
                optimal_pressure = Validator.validate_pressure(data['optimal_pressure'], unit=None, desired_unit=None)
                tire.optimal_pressure = optimal_pressure
                tire.pressure_unit = data['pressure_unit']

            db.session.commit()

            return jsonify({
                "message": f"Tire {tire_id} updated successfully",
                "tire_id": str(tire.tire_id)
            }), 200

        except ValueError as ve:
            db.session.rollback()
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to update tire"), 500


    @classmethod
    def get_vehicle_tires(cls, vehicle_id: str) -> tuple[Response, int]:
        """
        Get all tires for a specific vehicle with latest pressure readings.

        Args:
            vehicle_id: UUID of the vehicle

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            tires = cls.query.filter_by(vehicle_id=uuid.UUID(vehicle_id)).all()

            tires_data = []
            for tire in tires:
                latest_reading = PressureReading.get_latest_reading(str(tire.tire_id))

                tire_data = {
                    "tire_id": str(tire.tire_id),
                    "label": tire.label,
                    "optimal_pressure": float(tire.optimal_pressure),
                    "pressure_unit": tire.pressure_unit,
                    "sensor_code": tire.sensor_code,
                    "installed_at": tire.installed_at.isoformat(),
                    "current_alert_type": tire.current_alert_type,
                    "current_pressure": float(latest_reading.pressure_value) if latest_reading else None,
                    "pressure_updated_at": latest_reading.created_at.isoformat() if latest_reading else None
                }
                tires_data.append(tire_data)

            return jsonify({"tires": tires_data}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to get vehicle tires"), 500


    @classmethod
    def get_tire(cls, tire_id: str) -> tuple[Response, int]:
        """
        Get tire details by ID with latest pressure reading.

        Args:
            tire_id: UUID of the tire

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            tire = cls.query.get(uuid.UUID(tire_id))
            if not tire:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Tire {tire_id} not found",
                    status_code=404
                )

            latest_reading = PressureReading.get_latest_reading(tire_id)

            return jsonify({
                "tire_id": str(tire.tire_id),
                "vehicle_id": str(tire.vehicle_id),
                "label": tire.label,
                "optimal_pressure": float(tire.optimal_pressure),
                "pressure_unit": tire.pressure_unit,
                "sensor_code": tire.sensor_code,
                "installed_at": tire.installed_at.isoformat(),
                "current_alert_type": tire.current_alert_type,
                "current_pressure": float(latest_reading.pressure_value) if latest_reading else None,
                "pressure_updated_at": latest_reading.created_at.isoformat() if latest_reading else None
            }), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to get tire details"), 500


    @classmethod
    def delete_tire(cls, user_id: str, tire_id: str) -> tuple[Response, int]:
        """
        Delete a tire by ID.

        Args:
            user_id: UUID of the user
            tire_id: UUID of the tire to delete

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            tire = cls.query.get(uuid.UUID(tire_id))
            if not tire:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Tire {tire_id} not found",
                    status_code=404
                )

            # Check if the vehicle belongs to the user
            if tire.vehicle.user_id != user_id:
                return jsonify({"error": "Forbidden: You do not own this tire"}), 403

            db.session.delete(tire)
            db.session.commit()

            return jsonify({"message": f"Tire {tire_id} deleted successfully"}), 200

        except ValueError as ve:
            db.session.rollback()
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to delete tire"), 500
