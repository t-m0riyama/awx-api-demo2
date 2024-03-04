class RequestStatus():

    # const
    START = 'request start'
    APPROVED = 'request approved'
    APPLYING = 'request applying'
    COMPLETED = 'request completed'
    START_FRIENDLY = '申請中'
    APPROVED_FRIENDLY = '承認済み'
    APPLYING_FRIENDLY = '作業中'
    COMPLETED_FRIENDLY = '作業完了'

    FRIENDLY_MAP = {}
    FRIENDLY_MAP[START] = START_FRIENDLY
    FRIENDLY_MAP[APPROVED] = APPROVED_FRIENDLY
    FRIENDLY_MAP[APPLYING] = APPLYING_FRIENDLY
    FRIENDLY_MAP[COMPLETED] = COMPLETED_FRIENDLY

    @staticmethod
    def to_friendly(status):
        return RequestStatus.FRIENDLY_MAP[status]

    @staticmethod
    def to_formal(status_friendly):
        formal_map = {v: k for k, v in RequestStatus.FRIENDLY_MAP.items()}
        return formal_map[status_friendly]
