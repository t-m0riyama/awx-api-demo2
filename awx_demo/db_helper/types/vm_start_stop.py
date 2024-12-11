from awx_demo.utils.logging import Logging


class VmStartStop:

    # const
    STARTUP = 'startup_vm'
    SHUTDOWN = 'shutdown_vm'
    POWEROFF = 'poweroff_vm'
    STARTUP_FRIENDLY = '仮想マシンを起動する'
    SHUTDOWN_FRIENDLY = '仮想マシンを停止する'
    POWEROFF_FRIENDLY = '仮想マシンを電源OFFにする'

    FRIENDLY_MAP = {
        STARTUP: STARTUP_FRIENDLY,
        SHUTDOWN: SHUTDOWN_FRIENDLY,
        POWEROFF: POWEROFF_FRIENDLY,
    }

    @staticmethod
    @Logging.func_logger
    def to_friendly(status):
        return VmStartStop.FRIENDLY_MAP[status]

    @staticmethod
    @Logging.func_logger
    def to_formal(status_friendly):
        formal_map = {v: k for k, v in VmStartStop.FRIENDLY_MAP.items()}
        return formal_map[status_friendly]
