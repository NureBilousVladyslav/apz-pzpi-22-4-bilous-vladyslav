from flask import Blueprint, request
from models import Notification
from utils.auth_decorator import role_required

notification_bp = Blueprint('notification', __name__)


@notification_bp.route('/notifications/limit', methods=['Get'])
@role_required(['customer']) 
def get_notifications():
    user = request.current_user
    return Notification.get_user_notifications(user.user_id)


@notification_bp.route('/notifications_by_vehicle/vehicle/limit', methods=['Get'])
@role_required(['customer']) 
def get_notifications_by_vehicle():
    vehicle_id = request.args.get('vehicle')
    limit = request.args.get('limit')
    return Notification.get_vehicle_notifications(vehicle_id, limit)
