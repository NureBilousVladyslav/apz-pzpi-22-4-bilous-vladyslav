from flask import Blueprint, request
from models import PressureReading
from services import auth_service
from utils import ErrorHandler

iot_bp = Blueprint('iot', __name__)


@iot_bp.route('/add_reading', methods=['Post'])
def send_sensor_status():
    data = request.get_json()
    user = auth_service.login_user(data)
    if user:
        return PressureReading.add_reading(user.user_id, data)
    return ErrorHandler.handle_error(
        None,
        message="Invalid credentials",
        status_code=403
    )
