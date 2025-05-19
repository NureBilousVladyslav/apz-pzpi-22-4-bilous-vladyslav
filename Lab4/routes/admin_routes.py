from flask import Blueprint, request
from models import User
from utils.auth_decorator import role_required

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/users', methods=['Get'])
@role_required(['admin'])
def get_users():
    return User.get_users_by_role(role_name='customer')


@admin_bp.route('/user/user', methods=['Get'])
@role_required(['admin']) 
def get_user():
    user_id = request.args.get('user')
    return User.get_user(user_id)


@admin_bp.route('/delete_user/user', methods=['Delete'])
@role_required(['admin']) 
def delete_user():
    user_id = request.args.get('user')
    return User.delete_user(user_id)


@admin_bp.route('/admins', methods=['Get'])
@role_required(['admin'])
def get_admins():
    return User.get_users_by_role(role_name='admin')


@admin_bp.route('/register_admin', methods=['Post'])
@role_required(['admin'])
def register_admin():
    data = request.get_json()
    return User.register_user(data, role_name='admin')
