from enum import IntEnum, auto

from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.notification.teams_notificator import TeamsNotificator


class Notificator:
    # const
    TEAMS_NOTIFICATION = 0
    MAIL_NOTIFICATION = 1

    @staticmethod
    def notify(notification_spec: NotificationSpec):
        match notification_spec.notification_type:
            case Notificator.TEAMS_NOTIFICATION:
                TeamsNotificator.notify(notification_spec)
            # case Notificator.MAIL_NOTIFICATION:
            #     MailNotificator.notify(notification_spec)
