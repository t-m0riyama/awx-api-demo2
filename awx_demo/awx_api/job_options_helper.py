import os

from awx_demo.db_helper.types.request_category import RequestOperation
from awx_demo.utils.logging import Logging


class JobOptionsHelper:
    # const
    JOB_TEMPLATE_SET_VM_CPU_MEMORY_DEFAULT = 'vm-config-utils_set_vm_cpu'
    JOB_TEMPLATE_VM_START_STOP_DEFAULT = 'vm-config-utils_vm_start_stop'

    @staticmethod
    @Logging.func_logger
    def generate_job_options(session, request_operation):
        target_options = []
        match request_operation:
            case RequestOperation.VM_CPU_MEMORY_CAHNGE:
                target_options = [
                    'vsphere_cluster',
                    'target_vms',
                    'vcpus',
                    'memory_gb',
                    'change_vm_cpu_enabled',
                    'change_vm_memory_enabled',
                    'shutdown_before_change',
                    'startup_after_change',
                ]
            case RequestOperation.VM_START_OR_STOP:
                target_options = [
                    'vsphere_cluster',
                    'target_vms',
                    'vm_start_stop',
                    'vm_start_stop_enabled',
                    'shutdown_timeout_sec',
                    'tools_wait_timeout_sec',
                ]
        job_options = {}
        for key in target_options:
            if key in session.get('job_options'):
                job_options[key] = str(session.get('job_options')[key])
        return job_options

    @staticmethod
    @Logging.func_logger
    def get_job_template_name(request_operation):
        match request_operation:
            case RequestOperation.VM_CPU_MEMORY_CAHNGE:
                return os.getenv("JOB_TEMPLATE_SET_VM_CPU_MEMORY", JobOptionsHelper.JOB_TEMPLATE_SET_VM_CPU_MEMORY_DEFAULT)
            case RequestOperation.VM_START_OR_STOP:
                return os.getenv("JOB_TEMPLATE_VM_START_STOP", JobOptionsHelper.JOB_TEMPLATE_VM_START_STOP_DEFAULT)
