from flask import Blueprint, request
from models import Vehicle
from utils.auth_decorator import role_required

vehicle_bp = Blueprint('vehicle', __name__)


@vehicle_bp.route('/user_vehicles', methods=['Get'])
@role_required(['customer']) 
def get_user_vehicles():
    user = request.current_user
    return Vehicle.get_user_vehicles(user.user_id)


@vehicle_bp.route('/vehicle/vehicle', methods=['Get'])
@role_required(['customer'])
def get_vehicle():
    user = request.current_user
    vehicle_id = request.args.get('vehicle')
    return Vehicle.get_vehicle(vehicle_id)


@vehicle_bp.route('/add_vehicle', methods=['Post'])
@role_required(['customer']) 
def add_vehicle():
    user = request.current_user
    data = request.get_json()
    return Vehicle.add_vehicle(user.user_id, data)


@vehicle_bp.route('/delete_vehicle/vehicle', methods=['Delete'])
@role_required(['customer'])
def delete_vehicle():
    user = request.current_user
    vehicle_id = request.args.get('vehicle')
    return Vehicle.delete_vehicle(user.user_id, vehicle_id)


@vehicle_bp.route('/update_vehicle', methods=['Put'])
@role_required(['customer'])
def update_vehicle():
    user = request.current_user
    data = request.get_json()
    return Vehicle.update_vehicle(user.user_id, data)
