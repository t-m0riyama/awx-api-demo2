import os
import time

from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.notification.teams_notificator import TeamsNotificator


class Notificator:
    # const
    TEAMS_NOTIFICATION = 0
    MAIL_NOTIFICATION = 1

    @classmethod
    def notify(cls, notification_spec: NotificationSpec):
        match notification_spec.notification_type:
            case Notificator.TEAMS_NOTIFICATION:
                TeamsNotificator.notify(notification_spec)
                teams_webhook_message_delay_msec = int(os.getenv("RMX_TEAMS_WEB_HOOK_MESSAGE_DELAY_MSEC", 500))
                time.sleep(teams_webhook_message_delay_msec * 0.001)
            # case Notificator.MAIL_NOTIFICATION:
            #     MailNotificator.notify(notification_spec)
