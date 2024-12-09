from distutils.util import strtobool

import flet as ft

from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.logging import Logging


class SetVmStartStopTabForm(ft.Card):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_START_DESCRIPTION = '仮想マシンを起動する'
    VM_STOP_DESCRIPTION = '仮想マシンを停止する'
    VM_POWEROFF_DESCRIPTION = '仮想マシンを電源OFFにする'

    def __init__(self, session, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height

        # controls
        self.checkChangeStartStopEnabled = ft.Checkbox(
            label='起動/停止の状態を変更する',
            value=self.session.get('job_options')['change_vm_start_stop_enabled'] if 'change_vm_start_stop_enabled' in self.session.get('job_options') else True,
            on_change=self.on_change_vm_start_stop_enabled,
            disabled=True,
        )

        self.dropVmStartStop = ft.Dropdown(
            label='起動または停止',
            value=self.session.get('job_options')['vm_start_stop'] if 'vm_start_stop' in self.session.get('job_options') else self.VM_START_DESCRIPTION,
            options=[
                ft.dropdown.Option(self.VM_START_DESCRIPTION),
                ft.dropdown.Option(self.VM_STOP_DESCRIPTION),
                ft.dropdown.Option(self.VM_POWEROFF_DESCRIPTION),
            ],
            disabled=(not bool(strtobool(self.session.get('job_options')['change_vm_start_stop_enabled']))) if 'change_vm_start_stop_enabled' in self.session.get('job_options') else False,
        )
        self.tfShutdownTimeoutSec = ParameterInputText(
            value=self.session.get('job_options')['shutdown_timeout_sec'] if 'shutdown_timeout_sec' in self.session.get('job_options') else 600,
            label='シャットダウン時の待ち合わせ時間(秒)',
            text_align=ft.TextAlign.RIGHT,
            expand=True,
            hint_text='シャットダウンに時間を要するサーバは、この値をより大きく設定して下さい。',
            on_change=self.on_change_shutdown_timeout_sec,
        )
        self.tfToolsWaitTimeoutSec = ParameterInputText(
            value=self.session.get('job_options')['tools_wait_timeout_sec'] if 'tools_wait_timeout_sec' in self.session.get('job_options') else 600,
            label='VMware Tools起動の待ち合わせ時間(秒)',
            text_align=ft.TextAlign.RIGHT,
            expand=True,
            hint_text='起動に時間を要するサーバは、この値をより大きく設定して下さい。',
            on_change=self.on_change_tools_wait_timeout_sec,
        )

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get('user_role') == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                # formDescription,
                self.checkChangeStartStopEnabled,
                self.dropVmStartStop,
                ft.Row([
                    self.tfShutdownTimeoutSec,
                    self.tfToolsWaitTimeoutSec,
                ]),
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
    def generate_confirm_text(self):
        confirm_text = '== 基本情報 ====================='
        confirm_text += '\n依頼者(アカウント): ' + self.session.get('awx_loginid')
        confirm_text += '\n依頼内容: ' + (self.session.get('request_text') if self.session.contains_key(
            'request_text') and self.session.get('request_text') != '' else '(未指定)')
        confirm_text += '\n依頼区分: ' + self.session.get('request_category')
        confirm_text += '\n申請項目: ' + self.session.get('request_operation')
        request_deadline = self.session.get('request_deadline').strftime(
            '%Y/%m/%d') if self.session.contains_key('request_deadline') else '(未指定)'
        confirm_text += '\nリリース希望日: ' + request_deadline
        confirm_text += '\n\n== 詳細情報 ====================='
        confirm_text += '\nクラスタ: ' + \
            self.session.get('job_options')['vsphere_cluster']
        confirm_text += '\n仮想マシン: ' + \
            self.session.get('job_options')['target_vms']
        if str(self.session.get('job_options')['change_vm_start_stop_enabled']) == 'True':
            confirm_text += '\n起動/停止: ' + str(self.session.get('job_options')['vm_start_stop'])
            confirm_text += '\nシャットダウン時の待ち合わせ時間(秒): ' + str(self.session.get('job_options')['shutdown_timeout_sec'])
            confirm_text += '\nVMware Tools起動の待ち合わせ時間(秒): ' + str(self.session.get('job_options')['tools_wait_timeout_sec'])
        return confirm_text

    @Logging.func_logger
    def on_change_vm_start_stop_enabled(self, e):
        self.session.get('job_options')['change_vm_start_stop_enabled'] = str(e.control.value)
        self.dropVmStartStop.disabled = False if e.control.value else True
        self.tfShutdownTimeoutSec.disabled = False if e.control.value else True
        self.tfToolsWaitTimeoutSec.disabled = False if e.control.value else True
        self.dropVmStartStop.update()
        self.tfShutdownTimeoutSec.update()
        self.tfToolsWaitTimeoutSec.update()

    @Logging.func_logger
    def on_change_vm_start_stop(self, e):
        self.session.get('job_options')['vm_start_stop'] = self.dropVmStartStop.value

    @Logging.func_logger
    def on_change_shutdown_timeout_sec(self, e):
        self.session.get('job_options')['shutdown_timeout_sec'] = int(self.tfShutdownTimeoutSec.value)

    @Logging.func_logger
    def on_change_tools_wait_timeout_sec(self, e):
        self.session.get('job_options')['tools_wait_timeout_sec'] = int(self.tfToolsWaitTimeoutSec.value)