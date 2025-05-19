from models import User
from app import login_manager
from services.email_confirm_service import EmailConfirmService
from utils import ErrorHandler, JwtUtils
from flask import jsonify
import flask_login


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


def session_login_user(data):
    try:
        user = login_user(data)
        if user:
            flask_login.login_user(user)
            return jsonify({'message': 'Logged in successfully.'}), 200

        raise PermissionError('Invalid credentials.')

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except PermissionError as pe:
        return ErrorHandler.handle_error(pe, message=str(pe), status_code=403)
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error during session login",
            status_code=500
        )


def token_login_user(data):
    try:
        user = login_user(data)
        if user:
            token = JwtUtils.generate_jwt({'user_id': str(user.user_id)})
            return jsonify({'message': 'Logged in successfully.', 'token': token}), 200

        raise PermissionError('Invalid credentials.')

    except ValueError as ve:
        return ErrorHandler.handle_validation_error(str(ve))
    except PermissionError as pe:
        return ErrorHandler.handle_error(pe, message=str(pe), status_code=403)
    except RuntimeError as re:
        return ErrorHandler.handle_error(re, message=str(re), status_code=500)
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error during token login",
            status_code=500
        )


def login_user(data):
    email = data.get('email')
    if not email:
        raise ValueError("Email is required for login.")

    user = User.get_user_by_email(email)
    if not user:
        raise PermissionError('Invalid credentials.')

    if not user.email_confirmed:
        EmailConfirmService.send_email_confirmation(user)
        raise PermissionError("Please confirm your email first.")

    if user.check_password(data.get('password')):
        return user

    raise PermissionError('Invalid credentials.')


def logout_user():
    try:
        if flask_login.current_user.is_authenticated:
            flask_login.logout_user()
            return jsonify({'message': 'Logged out successfully.'}), 200
        else:
            return ErrorHandler.handle_error(
                None,
                message="No user logged in",
                status_code=401
            )
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while logout",
            status_code=500
        )


def verify_token(token: str | None) -> tuple[dict, int]:
    """
    Verify JWT token and return API-friendly response.

    Args:
        token: The 'Authorization' header content (may include 'Bearer ' prefix)

    Returns:
        tuple: (response_dict, status_code) where:
            - response_dict contains:
                - 'valid': bool indicating token validity
                - 'user_id': string (present when valid=True)
                - 'message': error description (present when valid=False)
            - status_code: HTTP status code (200, 401, or 500)

    Behavior:
        - Returns 401 if:
            - Token is missing
            - Token has invalid format
            - Token is expired/invalid
        - Returns 500 for unexpected server errors
        - Returns 200 with user_id for valid tokens
    """
    # Token presence check
    if not token:
        return {"valid": False, "message": "Token is missing"}, 401

    # Remove 'Bearer ' prefix if present
    clean_token = token[7:] if token.startswith("Bearer ") else token
    if not clean_token:
        return {"valid": False, "message": "Invalid token format"}, 401

    # Token validation
    try:
        payload = JwtUtils.decode_jwt(clean_token)
        return {
            "valid": True,
            "user_id": payload.get("user_id")
        }, 200
    except ValueError as e:
        return {"valid": False, "message": str(e)}, 401
    except Exception:
        return {"valid": False, "message": "Token verification failed"}, 500