from flask_mail import Message
from app import mail, app
from db import db
from config import Config
from models import User
import random
import string
from itsdangerous import URLSafeTimedSerializer
from flask import url_for, render_template, jsonify, Response
from utils import ErrorHandler

s = URLSafeTimedSerializer(Config.SECRET_KEY)


def reset_password_request(data: dict) -> tuple[Response, int]:
    """
    Handle a password reset request by sending a confirmation email with a token.

    Args:
        data (dict): Dictionary containing the user's email.
            - email (str): The email address of the user requesting a password reset.

    Returns:
        tuple[Response, int]: A tuple containing the JSON response and HTTP status code.
            - Success: ({"message": "The confirmation was sent successfully."}, 200)
            - Error: Response from ErrorHandler with appropriate status code (400, 404, 500).

    Raises:
        ValueError: If the email is not provided in the data.
        Exception: For unexpected errors during email sending.
    """
    try:
        if not data or not data.get('email'):
            raise ValueError("Email is required")

        user = User.get_user_by_email(data['email'])
        if not user:
            return ErrorHandler.handle_error(
                None,
                message=f"User with email '{data['email']}' not found.",
                status_code=404
            )

        token = s.dumps(user.email, salt='reset-password-confirm-salt')
        confirmation_url = url_for('user_profile.confirm_reset_password', token=token, _external=True)

        msg = Message(
            "Reset Password Confirmation",
            recipients=[user.email],
            body=f"To confirm your password reset, visit the following link: {confirmation_url}",
            html=render_template(
                "reset_password_confirmation.html",
                name=user.name,
                confirmation_url=confirmation_url
            )
        )

        mail.send(msg)
        return jsonify({'message': 'The confirmation was sent successfully.'}), 200

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending the password reset email.",
            status_code=500
        )


def verify_reset_password_token(token: str) -> str:
    """
    Verify the password reset token and initiate the password reset process.

    Args:
        token (str): The token received from the confirmation email.

    Returns:
        str: Rendered HTML template as a string.
            - Success: HTML from "reset_password_confirmation_success.html".
            - Error: HTML from "reset_password_confirmation_error.html" with an error message.

    Raises:
        PermissionError: If the token is invalid or expired.
        RuntimeError: If there's an error sending the reset email.
        Exception: For unexpected errors during token verification.
    """
    try:
        email = s.loads(token, salt='reset-password-confirm-salt', max_age=3600)
        user = User.query.filter_by(email=email).first()

        if user is None:
            raise PermissionError('The token is invalid or expired.')

        send_password_reset_email(user)

        return render_template(
            "reset_password_confirmation_success.html",
            user=user
        )

    except PermissionError as pe:
        return render_template(
            "reset_password_confirmation_error.html",
            error_message=str(pe)
        )

    except RuntimeError as re:
        return render_template(
            "reset_password_confirmation_error.html",
            error_message=str(re)
        )

    except Exception as e:
        return render_template(
            "reset_password_confirmation_error.html",
            error_message=f"Internal server error during reset password confirmation. {str(e)}"
        )


def send_password_reset_email(user: User) -> tuple[Response, int]:
    """
    Send an email with a new randomly generated password to the user.

    Args:
        user (User): The User object for whom the password is being reset.

    Returns:
        tuple[Response, int]: A tuple containing the JSON response and HTTP status code.
            - Success: ({"message": "A new password has been sent to your email."}, 200)
            - Error: Response from ErrorHandler with status code 400 or 500.

    Raises:
        RuntimeError: If there's an error sending the email.
        ValueError: If there's an issue with password validation or update.
        Exception: For unexpected errors during email sending.
    """
    try:
        new_password = generate_random_password()
        update_password(user, new_password)

        msg = Message(
            "Your New Password",
            recipients=[user.email],
            body=f"Your new password is: {new_password}\n"
                 f"You can log in using this password. Please change it after logging in.",
            html=render_template(
                "password_reset_email.html",
                name=user.name,
                new_password=new_password
            )
        )

        mail.send(msg)
        return jsonify({'message': 'A new password has been sent to your email.'}), 200

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except Exception as e:
        raise RuntimeError("Internal server error while sending the password reset email.") from e


def generate_random_password(length: int = 8) -> str:
    """
    Generate a random password of specified length.

    Args:
        length (int, optional): The length of the password. Defaults to 8.

    Returns:
        str: A randomly generated password consisting of letters and digits.

    Raises:
        Exception: If there's an error during password generation.
    """
    try:
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while generating the random password.",
            status_code=500
        )


def update_password(user: User, new_password: str) -> None:
    """
    Update the user's password in the database.

    Args:
        user (User): The User object whose password is being updated.
        new_password (str): The new password to set.

    Returns:
        None

    Raises:
        Exception: If there's an error updating the password in the database.
    """
    try:
        user.set_password(new_password)
        db.session.commit()
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while updating the user's password.",
            status_code=500
        )