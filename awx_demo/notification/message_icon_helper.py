import base64

from awx_demo.notification.notification_spec import NotificationSpec
from awx_demo.utils.event_helper import EventStatus
from awx_demo.utils.logging import Logging


class MessageIconHelper:

    # const
    INFORMATION_ICON_FILE = 'assets/images/information-icon.png'
    WARNING_ICON_FILE = 'assets/images/warning-icon.png'
    ERROR_ICON_FILE = 'assets/images/error-icon.png'

    @classmethod
    @Logging.func_logger
    def load_icon_to_base64(cls, notification_spec: NotificationSpec):
        icon_base64_byte: bytes = None

        if notification_spec.icon:
            # 明示的にアイコンのPNGファイルを指定した場合
            with open(notification_spec.icon, mode="rb") as f:
                icon_base64_byte = base64.b64encode(f.read())
        else:
            # 明示的にアイコンのPNGファイルを指定しなかった場合、ステータスをもとにアイコンを決定
            match notification_spec.status:
                case EventStatus.SUCCEED:
                    with open(cls.INFORMATION_ICON_FILE, mode="rb") as f:
                        icon_base64_byte = base64.b64encode(f.read())
                case EventStatus.WARNING:
                    with open(cls.WARNING_ICON_FILE, mode="rb") as f:
                        icon_base64_byte = base64.b64encode(f.read())
                case EventStatus.FAILED:
                    with open(cls.ERROR_ICON_FILE, mode="rb") as f:
                        icon_base64_byte = base64.b64encode(f.read())
        icon_base64: str = icon_base64_byte.decode('ascii')

        return icon_base64

    @classmethod
    @Logging.func_logger
    def get_icon_file_name(cls, notification_spec: NotificationSpec):
        if notification_spec.icon:
            return notification_spec.icon
        else:
            # 明示的にアイコンのPNGファイルを指定しなかった場合、ステータスをもとにアイコンを決定
            match notification_spec.status:
                case EventStatus.SUCCEED:
                    return cls.INFORMATION_ICON_FILE
                case EventStatus.WARNING:
                    return cls.WARNING_ICON_FILE
                case EventStatus.FAILED:
                    return cls.ERROR_ICON_FILE
