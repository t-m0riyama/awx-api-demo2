import os
import time

from awx_demo.notification.mail_notificator import MailNotificator
from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.notification.teams_adaptivecard_notificator import TeamsAdaptiveCardNotificator
from awx_demo.notification.teams_messagecard_notificator import TeamsMessageCardNotificator
from awx_demo.utils.logging import Logging


class Notificator:
    # const
    TEAMS_NOTIFICATION = 0
    MAIL_NOTIFICATION = 1

    TEAMS_MESSAGE_FORMAT_MESSAGE_CARD = "message_card"
    TEAMS_MESSAGE_FORMAT_ADAPTIVE_CARD = "adaptive_card"
    TEAMS_MESSAGE_FORMAT_DEFAULT = TEAMS_MESSAGE_FORMAT_ADAPTIVE_CARD

    @classmethod
    @Logging.func_logger
    def notify(cls, notification_spec: NotificationSpec):
        match notification_spec.notification_type:
            case Notificator.TEAMS_NOTIFICATION:
                teams_message_format = os.getenv("RMX_TEAMS_MESSAGE_FORMAT", cls.TEAMS_MESSAGE_FORMAT_DEFAULT)
                match teams_message_format:
                    case cls.TEAMS_MESSAGE_FORMAT_MESSAGE_CARD:
                        TeamsMessageCardNotificator.notify(notification_spec)
                    case cls.TEAMS_MESSAGE_FORMAT_ADAPTIVE_CARD:
                        TeamsAdaptiveCardNotificator.notify(notification_spec)
                teams_webhook_message_delay_msec = int(os.getenv("RMX_TEAMS_WEB_HOOK_MESSAGE_DELAY_MSEC", 500))
                time.sleep(teams_webhook_message_delay_msec * 0.001)
            case Notificator.MAIL_NOTIFICATION:
                MailNotificator.notify(notification_spec)
