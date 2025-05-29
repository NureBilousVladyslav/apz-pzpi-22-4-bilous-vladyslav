from db import db
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from datetime import datetime
from flask import jsonify, Response
from utils import ErrorHandler, Validator


class Vehicle(db.Model):
    __tablename__ = 'vehicle'

    vehicle_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.user_id', ondelete='CASCADE'), nullable=False)
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    user = db.relationship('User', back_populates='vehicles')
    tires = db.relationship('Tire', back_populates='vehicle', cascade="all, delete-orphan")


    @classmethod
    def add_vehicle(cls, user_id: str, data: dict) -> tuple[Response, int]:
        """
        Add a new vehicle for a user.

        Args:
            user_id: UUID of the user
            data: {
                'make': str,
                'model': str,
                'year': int
            }

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            # Validate input
            Validator.validate_required_fields(data, ['make', 'model', 'year'])

            # Validate year format
            year = data['year']
            if not isinstance(year, int) or year < 1900 or year > datetime.now().year + 1:
                raise ValueError("Invalid vehicle year")

            # Create vehicle
            vehicle = cls(
                user_id=user_id,
                make=data['make'].strip(),
                model=data['model'].strip(),
                year=year
            )

            db.session.add(vehicle)
            db.session.commit()

            return jsonify({
                "message": "Vehicle added successfully",
                "vehicle_id": str(vehicle.vehicle_id)
            }), 201

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to add vehicle"), 500


    @classmethod
    def delete_vehicle(cls, user_id: str, vehicle_id: str) -> tuple[Response, int]:
        """
        Delete a vehicle by ID, ensuring it belongs to the user.

        Args:
            vehicle_id: UUID of the vehicle to delete.
            user_id: UUID of the user making the request.

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            vehicle = cls.query.get(uuid.UUID(vehicle_id))
            if not vehicle:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Vehicle {vehicle_id} not found",
                    status_code=404
                )

            # Check if the vehicle belongs to the user
            if vehicle.user_id != user_id:
                return jsonify({"error": "Forbidden: You do not own this vehicle"}), 403

            db.session.delete(vehicle)
            db.session.commit()

            return jsonify({"message": f"Vehicle {vehicle_id} deleted successfully"}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to delete vehicle"), 500


    @classmethod
    def get_user_vehicles(cls, user_id: str) -> tuple[Response, int]:
        """
        Get all vehicles for a specific user.

        Args:
            user_id: UUID of the user

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            vehicles = cls.query.filter_by(user_id=user_id).all()

            vehicles_data = [{
                "vehicle_id": str(v.vehicle_id),
                "make": v.make,
                "model": v.model,
                "year": v.year,
                "created_at": v.created_at.isoformat(),
            } for v in vehicles]

            return jsonify({"vehicles": vehicles_data}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to get user vehicles"), 500


    @classmethod
    def get_vehicle(cls, vehicle_id: str) -> tuple[Response, int]:
        """
        Get vehicle details by ID.

        Args:
            vehicle_id: UUID of the vehicle

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            vehicle = cls.query.get(uuid.UUID(vehicle_id))
            if not vehicle:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Vehicle {vehicle_id} not found",
                    status_code=404
                )

            return jsonify({
                "vehicle_id": str(vehicle.vehicle_id),
                "user_id": str(vehicle.user_id),
                "make": vehicle.make,
                "model": vehicle.model,
                "year": vehicle.year,
                "created_at": vehicle.created_at.isoformat()
            }), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to get vehicle details"), 500


    @classmethod
    def update_vehicle(cls, user_id: str, data: dict) -> tuple[Response, int]:
        """
        Update vehicle information.

        Args:
            user_id: UUID of the user
            data: Dictionary with fields to update

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            vehicle_id = data.get('vehicle_id')
            vehicle = cls.query.get(uuid.UUID(vehicle_id))
            if not vehicle:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Vehicle {vehicle_id} not found",
                    status_code=404
                )

            # Check if the vehicle belongs to the user
            if vehicle.user_id != user_id:
                return jsonify({"error": "Forbidden: You do not own this vehicle"}), 403

            # Update fields if they exist in data
            if 'make' in data:
                vehicle.make = data['make'].strip()
            if 'model' in data:
                vehicle.model = data['model'].strip()
            if 'year' in data:
                year = data['year']
                if not isinstance(year, int) or year < 1900 or year > datetime.now().year + 1:
                    raise ValueError("Invalid vehicle year")
                vehicle.year = year

            db.session.commit()

            return jsonify({
                "message": f"Vehicle {vehicle_id} updated successfully",
                "vehicle_id": str(vehicle.vehicle_id)
            }), 200

        except ValueError as ve:
            db.session.rollback()
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to update vehicle"), 500
