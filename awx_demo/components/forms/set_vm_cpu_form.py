import os
from distutils.util import strtobool

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.utils.logging import Logging


class SetVmCpuForm(ft.Card):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_CPUS_DEFAULT = '1,2,4,6,8'

    def __init__(self, session, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel

        # controls
        formTitle = FormTitle('CPUの割り当て変更', '変更内容')
        formDescription = FormDescription('仮想マシンに割り当てるCPUコア数を変更します。')
        self.checkChangeVmCpuEnabled = ft.Checkbox(
            label='CPUコア数を変更する',
            value=self.session.get('job_options')['change_vm_cpu_enabled'] if 'change_vm_cpu_enabled' in self.session.get('job_options') else True,
            on_change=self.on_change_vm_cpu_enabled,
        )

        # 選択可能なCPUコア数の決定
        vm_cpus = os.getenv('RMX_VM_CPUS', self.VM_CPUS_DEFAULT).strip('"').strip('\'')
        vm_cpu_options = []
        for vm_cpu_option in vm_cpus.split(","):
            vm_cpu_options.append(ft.dropdown.Option(vm_cpu_option.strip()))

        self.dropCpus = ft.Dropdown(
            label='CPUコア数',
            value=self.session.get('job_options')['vcpus'] if 'vcpus' in self.session.get('job_options') else '2',
            options=vm_cpu_options,
            disabled=(not bool(strtobool(self.session.get('job_options')['change_vm_cpu_enabled']))) if 'change_vm_cpu_enabled' in self.session.get('job_options') else False,
        )
        self.btnNext = ft.FilledButton(
            '次へ', on_click=self.on_click_next)
        self.btnPrev = ft.ElevatedButton(
            '戻る', on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            'キャンセル', on_click=self.on_click_cancel)

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
                self.checkChangeVmCpuEnabled,
                self.dropCpus,
            ],
            height=self.body_height,
        )
        footer = ft.Row(
            [
                self.btnCancel,
                self.btnPrev,
                self.btnNext,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        controls = ft.Container(
            ft.Column(
                [
                    header,
                    body,
                    ft.Divider(),
                    footer,
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
    def on_click_cancel(self, e):
        self.step_change_cancel(e)

    @Logging.func_logger
    def on_click_previous(self, e):
        self.step_change_previous(e)

    @Logging.func_logger
    def on_click_next(self, e):
        self.session.get('job_options')['change_vm_cpu_enabled'] = str(self.checkChangeVmCpuEnabled.value)
        self.session.get('job_options')['vcpus'] = int(self.dropCpus.value)
        self.step_change_next(e)
