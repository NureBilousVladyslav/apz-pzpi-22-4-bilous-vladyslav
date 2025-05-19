from flask import Blueprint, request
from models import Tire
from utils.auth_decorator import role_required

tire_bp = Blueprint('tire', __name__)


@tire_bp.route('/vehicle_tires/vehicle', methods=['Get'])
@role_required(['customer']) 
def get_vehicle_tires():
    user = request.current_user
    vehicle_id = request.args.get('vehicle')
    return Tire.get_vehicle_tires(vehicle_id)


@tire_bp.route('/tire/tire', methods=['Get'])
@role_required(['customer']) 
def get_tire():
    user = request.current_user
    tire_id = request.args.get('tire')
    return Tire.get_tire(tire_id)


@tire_bp.route('/add_tire', methods=['Post'])
@role_required(['customer']) 
def add_tire():
    user = request.current_user
    data = request.get_json()
    return Tire.add_tire(user.user_id, data)


@tire_bp.route('/delete_tire/tire', methods=['Delete'])
@role_required(['customer']) 
def delete_tire():
    user = request.current_user
    tire_id = request.args.get('tire')
    return Tire.delete_tire(user.user_id, tire_id)


@tire_bp.route('/update_tire', methods=['Put'])
@role_required(['customer']) 
def update_tire():
    user = request.current_user
    data = request.get_json()
    return Tire.update_tire(user.user_id, data)