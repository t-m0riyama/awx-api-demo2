from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.notification.notificator import Notificator


class EventManager:

    @classmethod
    def emit_event(cls, activity_spec: ActivityHelper.ActivitySpec, notification_specs: list[NotificationSpec]):
        ActivityHelper.add_activity(
            activity_spec
        )
        for notification_spec in notification_specs:
            Notificator.notify(
                notification_spec
            )
