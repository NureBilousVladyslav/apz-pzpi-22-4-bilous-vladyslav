from db import db
import uuid
from sqlalchemy.dialects.postgresql import UUID
from flask_login import UserMixin
from sqlalchemy.sql import func
from datetime import datetime
from flask import jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from models.role_model import Role
from utils import ErrorHandler, Validator


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role_id = db.Column(UUID(as_uuid=True), db.ForeignKey('role.role_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birthday = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    email_confirmed = db.Column(db.Boolean, default=False)

    role = db.relationship('Role', back_populates='users')
    vehicles = db.relationship(
        'Vehicle',
        back_populates='user',
        cascade="all, delete-orphan"
    )

    def get_id(self):
        return self.user_id

    def set_password(self, password: str) -> None:
        """Set hashed password for the user."""
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check if provided password matches the stored hash."""
        return check_password_hash(self.password, password)


    @staticmethod
    def get_user_by_email(email):
        user = User.query.filter_by(email=email).first()
        return user


    @classmethod
    def register_user(cls, data: dict, role_name: str) -> tuple[Response, int]:
        """
        Register a new user with specified role.

        Args:
            data (dict): User data containing name, email, password, and optional birthday
            role_name (str): Name of the role to assign

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            # Extract data safely
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')
            birthday = data.get('birthday')  # Optional field

            # Validate required fields
            Validator.validate_required_fields(data, ['name', 'email', 'password'])
            Validator.validate_email(email)
            Validator.validate_name(name)
            Validator.validate_password(password)
            Validator.validate_birthday(birthday)

            # Check existing user
            if cls.query.filter_by(email=email).first():
                return ErrorHandler.handle_error(
                    None,
                    message="User already exists",
                    status_code=409
                )

            # Get role
            role = Role.query.filter_by(role_name=role_name).first()
            if not role:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Role '{role_name}' not found",
                    status_code=404
                )

            # Create user
            user = cls(
                name=name,
                email=email,
                role_id=role.role_id,
                birthday=datetime.strptime(birthday, '%Y-%m-%d').date() if birthday else None
            )
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            from services.email_confirm_service import EmailConfirmService  
            EmailConfirmService.send_email_confirmation(user)

            return jsonify({"message": "User registered successfully."}), 201

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to register user"), 500


    @classmethod
    def get_users_by_role(cls, role_name: str) -> tuple[Response, int]:
        """
        Get all users with a specific role.

        Args:
            role_name (str): Name of the role to filter users by

        Returns:
            tuple: (JSON response with list of users, HTTP status code)
        """
        try:
            role = Role.query.filter_by(role_name=role_name).first()
            if not role:
                return ErrorHandler.handle_error(
                    None,
                    message=f"Role '{role_name}' not found",
                    status_code=404
                )

            users = cls.query.filter_by(role_id=role.role_id).all()

            users_data = [
                {
                    "user_id": str(user.user_id),
                    "name": user.name,
                    "email": user.email,
                    "role": role_name,
                    "birthday": user.birthday.isoformat() if user.birthday else None,
                    "created_at": user.created_at.isoformat(),
                    "email_confirmed": user.email_confirmed
                } for user in users
            ]

            return jsonify({"users": users_data}), 200

        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to fetch users by role"), 500


    @classmethod
    def get_user(cls, user_id: str) -> tuple[Response, int]:
        """
        Get user information by ID.

        Args:
            user_id (str): UUID of the user

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return ErrorHandler.handle_error(
                    None,
                    message="User not found",
                    status_code=404
                )

            user_data = {
                "user_id": str(user.user_id),
                "name": user.name,
                "email": user.email,
                "birthday": user.birthday.isoformat() if user.birthday else None,
                "role": user.role.role_name,
                "created_at": user.created_at.isoformat(),
                "email_confirmed": user.email_confirmed,
                "vehicles_count": len(user.vehicles),
            }
            return jsonify({"user": user_data}), 200

        except ValueError:
            return ErrorHandler.handle_validation_error("Invalid user ID format"), 400
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to fetch user"), 500


    @classmethod
    def delete_user(cls, user_id: str) -> tuple[Response, int]:
        """
        Delete a user by ID.

        Args:
            user_id (str): UUID of the user to delete

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return ErrorHandler.handle_error(
                    None,
                    message="User not found",
                    status_code=404
                )

            db.session.delete(user)
            db.session.commit()
            return jsonify({"message": f"User {user_id} deleted successfully"}), 200

        except ValueError:
            return ErrorHandler.handle_validation_error("Invalid user ID format"), 400
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to delete user"), 500


    @classmethod
    def get_user_by_id(cls, user_id: str) -> tuple[Response, int]:
        """
        Get detailed user information by ID.

        Args:
            user_id (str): UUID of the user

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return ErrorHandler.handle_error(
                    None,
                    message="User not found",
                    status_code=404
                )

            return jsonify({
                "user_id": str(user.user_id),
                "name": user.name,
                "email": user.email,
                "birthday": user.birthday.isoformat() if user.birthday else None,
                "role": user.role.role_name,
                "created_at": user.created_at.isoformat(),
                "email_confirmed": user.email_confirmed,
                "vehicles_count": len(user.vehicles),
            }), 200

        except ValueError:
            return ErrorHandler.handle_validation_error("Invalid user ID format"), 400
        except Exception as e:
            return ErrorHandler.handle_error(e, "Failed to fetch user information"), 500


    @classmethod
    def update_password(cls, user_id: str, data: dict) -> tuple[Response, int]:
        """
        Update user's password.

        Args:
            user_id (str): UUID of the user
            data (dict): Dictionary containing old_password and new_password

        Returns:
            tuple: (JSON response, HTTP status code)
        """
        try:
            old_password = data.get('old_password')
            new_password = data.get('new_password')

            Validator.validate_required_fields(data, ['old_password', 'new_password'])
            Validator.validate_password(new_password)

            user = User.query.filter_by(user_id=user_id).first()
            if not user:
                return ErrorHandler.handle_error(None, message="User not found", status_code=404)

            if not user.check_password(old_password):
                raise ValueError("Invalid old password.")

            user.set_password(new_password)
            db.session.commit()

            return jsonify({"message": f"Password for user {user_id} updated successfully"}), 200

        except ValueError as ve:
            return ErrorHandler.handle_validation_error(str(ve))
        except Exception as e:
            db.session.rollback()
            return ErrorHandler.handle_error(e, "Failed to update password"), 500


    @staticmethod
    def verify_email(user):
        user.email_confirmed = True
        db.session.commit()