from enum import IntEnum, auto


class NotificationSpec:

    def __init__(self, notification_type, title, sub_title, sub_title2=None, user=None, request_id=None, event_type=None, status=None, summary=None, detail=None, request_text=None, request_deadline=None, icon=None):
        self.notification_type = notification_type
        self.title = title
        self.sub_title = sub_title
        self.sub_title2 = sub_title2
        self.user = user
        self.request_id = request_id
        self.event_type = event_type
        self.status = status
        self.summary = summary
        self.detail = detail
        self.request_text = request_text
        self.request_deadline = request_deadline
        self.icon = icon


class NotificationMethod(IntEnum):
    NOTIFY_NONE = auto()
    NOTIFY_TEAMS_ONLY = auto()
    NOTIFY_MAIL_ONLY = auto()
    NOTIFY_TEAMS_AND_MAIL = auto()
