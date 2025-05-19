from services.email_confirm_service import EmailConfirmService
from flask import Blueprint, request
from models import User
from services import auth_service, password_reset_service
from flask_login import login_required


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    return User.register_user(data, role_name='customer')


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    return auth_service.session_login_user(data)


@auth_bp.route('/token_login', methods=['POST'])
def token_login():
    data = request.get_json()
    return auth_service.token_login_user(data)


@auth_bp.route('/verify_token', methods=['GET'])
def verify_token():
    token = request.headers.get('Authorization')
    return auth_service.verify_token(token)


@auth_bp.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    return EmailConfirmService.verify_email_token(token)


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    return auth_service.logout_user()


@auth_bp.route('/reset_password', methods=['POST'])
def reset_password_request():
    data = request.get_json()
    return password_reset_service.reset_password_request(data)


@auth_bp.route('/confirm_reset_password/<token>', methods=['GET'])
def confirm_reset_password(token):
    return password_reset_service.verify_reset_password_token(token)
