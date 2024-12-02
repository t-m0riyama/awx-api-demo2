from awx_demo.utils.logging import Logging


class RequestStatus:

    # const
    START = 'request start'
    APPROVED = 'request approved'
    APPLYING = 'request applying'
    APPLYING_FAILED = 'request applying failed'
    COMPLETED = 'request completed'
    START_FRIENDLY = '申請中'
    APPROVED_FRIENDLY = '承認済み'
    APPLYING_FRIENDLY = '作業中'
    APPLYING_FAILED_FRIENDLY = '作業中(失敗)'
    COMPLETED_FRIENDLY = '作業完了'

    FRIENDLY_MAP = {
        START: START_FRIENDLY,
        APPROVED: APPROVED_FRIENDLY,
        APPLYING: APPLYING_FRIENDLY,
        APPLYING_FAILED: APPLYING_FAILED_FRIENDLY,
        COMPLETED: COMPLETED_FRIENDLY,
    }

    @staticmethod
    @Logging.func_logger
    def to_friendly(status):
        return RequestStatus.FRIENDLY_MAP[status]

    @staticmethod
    @Logging.func_logger
    def to_formal(status_friendly):
        formal_map = {v: k for k, v in RequestStatus.FRIENDLY_MAP.items()}
        return formal_map[status_friendly]
