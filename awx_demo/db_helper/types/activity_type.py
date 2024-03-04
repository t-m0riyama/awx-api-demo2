class ActivityStatus():

    # const
    SUCCEED = 'succeed'
    FAILED = 'failed'
    UNKNOWN = 'unknown'
    SUCCEED_FRIENDLY = '成功'
    FAILED_FRIENDLY = '失敗'
    UNKNOWN_FRIENDLY = '不明'

    FRIENDLY_MAP = {}
    FRIENDLY_MAP[SUCCEED] = SUCCEED_FRIENDLY
    FRIENDLY_MAP[FAILED] = FAILED_FRIENDLY
    FRIENDLY_MAP[UNKNOWN] = UNKNOWN_FRIENDLY

    @staticmethod
    def to_friendly(activity_status):
        return ActivityStatus.FRIENDLY_MAP[activity_status]

    @staticmethod
    def to_formal(activity_status_friendly):
        formal_map = {v: k for k, v in ActivityStatus.FRIENDLY_MAP.items()}
        return formal_map[activity_status_friendly]


class ActivityType():

    # const
    LOGIN = 'login'
    LOGOUT = 'logout'
    REQUEST_SENT = 'request sent'
    REQUEST_CHANGED = 'request changed'
    REQUEST_IAAS_USER_ASSIGNED = 'request iaas user assigned'
    REQUEST_STATUS_CHANGED = 'request status changed'
    REQUEST_EXECUTE_STARTED = 'request executed'
    REQUEST_EXECUTE_COMPLETED = 'request completed'
    REQUEST_DELETED = 'request deleted'
    GLOBAL_SETTING_CHANGED = 'global setting changed'
    LOGIN_FRIENDLY = 'ログイン'
    LOGOUT_FRIENDLY = 'ログアウト'
    REQUEST_SENT_FRIENDLY = '申請の作成'
    REQUEST_CHANGED_FRIENDLY = '申請内容の変更'
    REQUEST_IAAS_USER_ASSIGNED_FRIENDLY = '作業担当者の変更'
    REQUEST_STATUS_CHANGED_FRIENDLY = '申請状態の変更'
    REQUEST_EXECUTE_STARTED_FRIENDLY = '実行要求の送信'
    REQUEST_EXECUTE_COMPLETED_FRIENDLY = 'ジョブの実行'
    REQUEST_DELETED_FRIENDLY = '申請の削除'
    GLOBAL_SETTING_CHANGED_FRIENDLY = 'グローバル設定の変更'

    FRIENDLY_MAP = {}
    FRIENDLY_MAP[LOGIN] = LOGIN_FRIENDLY
    FRIENDLY_MAP[LOGOUT] = LOGOUT_FRIENDLY
    FRIENDLY_MAP[REQUEST_SENT] = REQUEST_SENT_FRIENDLY
    FRIENDLY_MAP[REQUEST_CHANGED] = REQUEST_CHANGED_FRIENDLY
    FRIENDLY_MAP[REQUEST_IAAS_USER_ASSIGNED] = REQUEST_IAAS_USER_ASSIGNED_FRIENDLY
    FRIENDLY_MAP[REQUEST_STATUS_CHANGED] = REQUEST_STATUS_CHANGED_FRIENDLY
    FRIENDLY_MAP[REQUEST_EXECUTE_STARTED] = REQUEST_EXECUTE_STARTED_FRIENDLY
    FRIENDLY_MAP[REQUEST_EXECUTE_COMPLETED] = REQUEST_EXECUTE_COMPLETED_FRIENDLY
    FRIENDLY_MAP[REQUEST_DELETED] = REQUEST_DELETED_FRIENDLY

    @staticmethod
    def to_friendly(activity_type):
        return ActivityType.FRIENDLY_MAP[activity_type]

    @staticmethod
    def to_formal(activity_type_friendly):
        formal_map = {v: k for k, v in ActivityType.FRIENDLY_MAP.items()}
        return formal_map[activity_type_friendly]
