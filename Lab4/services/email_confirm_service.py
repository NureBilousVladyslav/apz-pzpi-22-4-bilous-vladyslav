from models import User
from app import mail
from config import Config
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import url_for, render_template, jsonify, Response
from utils import ErrorHandler

s = URLSafeTimedSerializer(Config.SECRET_KEY)

class EmailConfirmService:
    @staticmethod
    def send_email_confirmation(user: User) -> tuple[Response, int]:
        """
        Send an email confirmation link to the user.

        Args:
            user (User): The User object for whom the email confirmation is being sent.

        Returns:
            tuple[Response, int]: A tuple containing the JSON response and HTTP status code.
                - Success: ({"message": "The email confirmation was sent successfully."}, 200)
                - Error: Response from ErrorHandler with status code 500.

        Raises:
            Exception: For unexpected errors during email sending.
        """
        try:
            token = s.dumps(user.email, salt='email-confirm-salt')
            confirmation_url = url_for('auth.confirm_email', token=token, _external=True)

            msg = Message(
                "Email Confirmation",
                recipients=[user.email],
                body=f"To confirm your email address, visit the following link: {confirmation_url}",
                html=render_template(
                    "email_confirmation.html",
                    name=user.name,
                    confirmation_url=confirmation_url
                )
            )

            mail.send(msg)
            return jsonify({'message': 'The email confirmation was sent successfully.'}), 200

        except Exception as e:
            return ErrorHandler.handle_error(
                e,
                message="Internal server error while sending the email confirmation.",
                status_code=500
            )

    @staticmethod
    def send_user_registered_email(user: User, password: str) -> tuple[Response, int]:
        """
        Send a registration notification email to the user with their role and temporary password.

        Args:
            user (User): The User object who has been registered.
            password (str): The temporary password assigned to the user.

        Returns:
            tuple[Response, int]: A tuple containing the JSON response and HTTP status code.
                - Success: ({"message": "User registered notification was sent successfully."}, 200)
                - Error: Response from ErrorHandler with status code 500.

        Raises:
            Exception: For unexpected errors during email sending.
        """
        try:
            token = s.dumps(user.email, salt='email-confirm-salt')
            confirmation_url = url_for('auth.confirm_email', token=token, _external=True)

            msg = Message(
                "User Registration Notification",
                recipients=[user.email],
                body=f"You were registered as {user.role.role_name} with password: {password}!\n"
                     f"To confirm your email address, visit the following link: {confirmation_url}",
                html=render_template(
                    "user_registered_notification.html",
                    name=user.name,
                    email=user.email,
                    role=user.role.role_name,
                    password=password,
                    confirmation_url=confirmation_url
                )
            )

            mail.send(msg)
            return jsonify({'message': 'User registered notification was sent successfully.'}), 200

        except Exception as e:
            return ErrorHandler.handle_error(
                e,
                message="Internal server error while sending the user registered notification.",
                status_code=500
            )

    @staticmethod
    def verify_email_token(token: str) -> str:
        """
        Verify the email confirmation token and confirm the user's email.

        Args:
            token (str): The token received from the confirmation email.

        Returns:
            str: Rendered HTML template as a string.
                - Success: HTML from "email_confirmation_success.html".
                - Error: HTML from "email_confirmation_error.html" with an error message.

        Raises:
            PermissionError: If the token is invalid or expired.
            RuntimeError: If there's an error during email verification.
            Exception: For unexpected errors during token verification.
        """
        try:
            email = s.loads(token, salt='email-confirm-salt', max_age=3600)
            user = User.query.filter_by(email=email).first()

            if user is None:
                raise PermissionError('The token is invalid or expired.')

            User.verify_email(user)

            return render_template(
                "email_confirmation_success.html",
                user=user
            )

        except PermissionError as pe:
            return render_template(
                "email_confirmation_error.html",
                error_message=str(pe)
            )

        except RuntimeError as re:
            return render_template(
                "email_confirmation_error.html",
                error_message=str(re)
            )

        except Exception as e:
            return render_template(
                "email_confirmation_error.html",
                error_message=f"Internal server error during email confirmation. {str(e)}"
            )