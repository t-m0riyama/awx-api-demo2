from awx_demo.utils.logging import Logging


class RequestCategory:

    # const
    VM_CREATE = "vm create"
    VM_SETTING_CHANGE = "vm setting change"
    BACKUP_STOP_OR_RESUME = "backup stop or resume"
    PRIVILEGED_ID_CREATE = "privileged id create"

    VM_CREATE_FRIENDLY = "新規サーバの構築"
    VM_SETTING_CHANGE_FRIENDLY = "サーバに対する変更"
    BACKUP_STOP_OR_RESUME_FRIENDLY = "バックアップの停止/再開"
    PRIVILEGED_ID_CREATE_FRIENDLY = "特権IDの払い出し"

    FRIENDLY_MAP = {
        VM_CREATE: VM_CREATE_FRIENDLY,
        VM_SETTING_CHANGE: VM_SETTING_CHANGE_FRIENDLY,
        BACKUP_STOP_OR_RESUME: BACKUP_STOP_OR_RESUME_FRIENDLY,
        PRIVILEGED_ID_CREATE: PRIVILEGED_ID_CREATE_FRIENDLY,
    }

    @staticmethod
    @Logging.func_logger
    def to_friendly(status):
        return RequestCategory.FRIENDLY_MAP[status]

    @staticmethod
    @Logging.func_logger
    def to_formal(status_friendly):
        formal_map = {v: k for k, v in RequestCategory.FRIENDLY_MAP.items()}
        return formal_map[status_friendly]


class RequestOperation:

    # const
    VM_CPU_MEMORY_CAHNGE = "vm cpu memory change"
    VM_START_OR_STOP = "vm start or stop"
    VM_SNAPSHOT_OPERATION = "vm snapshot operation"

    VM_CPU_MEMORY_CAHNGE_FRIENDLY = "CPUコア/メモリ割り当て変更"
    VM_START_OR_STOP_FRIENDLY = "サーバの起動/停止"
    VM_SNAPSHOT_OPERATION_FRIENDLY = "スナップショットの操作"

    FRIENDLY_MAP = {
        VM_CPU_MEMORY_CAHNGE: VM_CPU_MEMORY_CAHNGE_FRIENDLY,
        VM_START_OR_STOP: VM_START_OR_STOP_FRIENDLY,
        VM_SNAPSHOT_OPERATION: VM_SNAPSHOT_OPERATION_FRIENDLY,
    }

    @staticmethod
    @Logging.func_logger
    def to_friendly(status):
        return RequestOperation.FRIENDLY_MAP[status]

    @staticmethod
    @Logging.func_logger
    def to_formal(status_friendly):
        formal_map = {v: k for k, v in RequestOperation.FRIENDLY_MAP.items()}
        return formal_map[status_friendly]
