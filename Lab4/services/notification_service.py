from utils import ErrorHandler
from models.notification_model import Notification
from models.alert_type_model import AlertType

def send_alert_type_change_notification(user_id, tire, old_alert_type, new_alert_type):
    try:
        # Get alert type objects for notification
        old_alert = AlertType.query.get(old_alert_type) if old_alert_type else None
        new_alert = AlertType.query.get(new_alert_type)

        title = f"Tire status changed to {new_alert.alert_type}"
        body = f"Your tire '{tire.label}' status changed to {new_alert.alert_type}, {new_alert.description}."

        # Create notification
        Notification.add_notification(
            tire_id=tire.tire_id,
            old_alert_type=old_alert_type,
            new_alert_type=new_alert_type,
            title=title,
            body=body
        )

    except ValueError as ve:
        print(ErrorHandler.handle_validation_error(str(ve)))
    except Exception as e:
        return ErrorHandler.handle_error(
            e,
            message="Internal server error while sending security mode change notification.",
            status_code=500
        )
