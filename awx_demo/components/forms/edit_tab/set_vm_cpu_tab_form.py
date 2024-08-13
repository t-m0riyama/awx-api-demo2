import os

import flet as ft

from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.logging import Logging


class SetVmCpuTabForm(ft.Card):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_CPUS_DEFAULT = '1,2,4,6,8'

    def __init__(self, session, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height

        # controls
        self.checkChangeVmCpuEnabled = ft.Checkbox(
            label='CPUコア数を変更する',
            value=self.session.get('job_options')['change_vm_cpu_enabled'] if 'change_vm_cpu_enabled' in self.session.get('job_options') else True,
            on_change=self.on_change_vm_cpu_enabled,
        )

        # 選択可能なCPUコア数の決定
        vm_cpus = os.getenv('RMX_VM_CPUS', self.VM_CPUS_DEFAULT).strip('"')
        vm_cpu_options = []
        for vm_cpu_option in vm_cpus.split(","):
            vm_cpu_options.append(ft.dropdown.Option(vm_cpu_option.strip()))

        self.dropCpus = ft.Dropdown(
            label='CPUコア数',
            value=self.session.get('job_options')['vcpus'] if 'vcpus' in self.session.get('job_options') else '2',
            options=vm_cpu_options,
            on_change=self.on_change_dropcpus,
            disabled=(not self.session.get('job_options')['change_vm_cpu_enabled']) if 'change_vm_cpu_enabled' in self.session.get('job_options') else False,
        )

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get(
            'user_role') == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                self.checkChangeVmCpuEnabled,
                self.dropCpus,
            ],
            height=self.body_height,
            disabled=change_disabled,
        )

        controls = ft.Container(
            ft.Column(
                [
                    body,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=self.content_width,
            height=self.content_height,
            padding=30,
        )
        super().__init__(controls)

    @Logging.func_logger
    def on_change_vm_cpu_enabled(self, e):
        self.session.get('job_options')['change_vm_cpu_enabled'] = str(e.control.value)
        self.dropCpus.disabled = False if e.control.value else True
        self.dropCpus.update()

    @Logging.func_logger
    def on_change_dropcpus(self, e):
        self.session.get('job_options')['vcpus'] = int(self.dropCpus.value)
