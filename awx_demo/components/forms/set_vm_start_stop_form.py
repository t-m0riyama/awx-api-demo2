from distutils.util import strtobool

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.utils.logging import Logging


class SetVmStartStopForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_START_DESCRIPTION = '仮想マシンを起動する'
    VM_STOP_DESCRIPTION = '仮想マシンを停止する'
    VM_POWEROFF_DESCRIPTION = '仮想マシンを電源OFFにする'

    def __init__(self, session, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel

        # controls
        formTitle = FormTitle('仮想マシンの起動/停止', '変更内容')
        formDescription = FormDescription('仮想マシンを起動または停止します。')
        self.checkChangeStartStopEnabled = ft.Checkbox(
            label='起動/停止の状態を変更する',
            value=self.session.get('job_options')['change_vm_start_stop_enabled'] if 'change_vm_start_stop_enabled' in self.session.get('job_options') else True,
            on_change=self.on_change_vm_start_stop_enabled,
        )

        self.dropStartStop = ft.Dropdown(
            label='起動または停止',
            value=self.session.get('job_options')[
                'change_vm_start_stop_enabled'] if 'change_vm_start_stop_enabled' in self.session.get('job_options') else self.VM_START_DESCRIPTION,
            options=[
                ft.dropdown.Option(self.VM_START_DESCRIPTION),
                ft.dropdown.Option(self.VM_STOP_DESCRIPTION),
                ft.dropdown.Option(self.VM_POWEROFF_DESCRIPTION),
            ],
            disabled=(not bool(strtobool(self.session.get('job_options')['change_vm_start_stop_enabled']))) if 'change_vm_start_stop_enabled' in self.session.get('job_options') else False,
        )
        self.tfShutdownTimeoutSec = ParameterInputText(
            value=self.session.get('shutdown_timeout_sec') if self.session.contains_key(
                'shutdown_timeout_sec') else 600,
            label='シャットダウン時の待ち合わせ時間(秒)',
            text_align=ft.TextAlign.RIGHT,
            hint_text='シャットダウンに時間を要するサーバは、この値をより大きく設定して下さい。')
        self.tfToolsWaitTimeoutSec = ParameterInputText(
            value=self.session.get('tools_wait_timeout_sec') if self.session.contains_key(
                'tools_wait_timeout_sec') else 600,
            label='VMware Tools起動の待ち合わせ時間(秒)',
            text_align=ft.TextAlign.RIGHT,
            hint_text='起動に時間を要するサーバは、この値をより大きく設定して下さい。')
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
                self.checkChangeStartStopEnabled,
                self.dropStartStop,
                self.tfShutdownTimeoutSec,
                self.tfToolsWaitTimeoutSec,
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

        self.controls = ft.Container(
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
        super().__init__(self.controls)

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
        return confirm_text

    @Logging.func_logger
    def on_change_vm_start_stop_enabled(self, e):
        self.session.get('job_options')['change_vm_start_stop_enabled'] = str(e.control.value)
        self.dropStartStop.disabled = False if e.control.value else True
        self.dropStartStop.update()

    @Logging.func_logger
    def on_click_next(self, e):
        self._lock_form_controls()
        self.session.get('job_options')['change_vm_start_stop_enabled'] = str(self.checkChangeStartStopEnabled.value)
        self.session.get('job_options')['vm_start_stop'] = self.dropStartStop.value
        self.session.set('confirm_text', self.generate_confirm_text())
        Logging.info('JOB_OPTIONS: ' + str(self.session.get('job_options')))
        self._unlock_form_controls()
        self.step_change_next(e)
