from distutils.util import strtobool

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.db_helper.types.vm_start_stop import VmStartStop
from awx_demo.utils.logging import Logging


class SetVmStartStopForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_START_DESCRIPTION = '仮想マシンを起動する'
    VM_STOP_DESCRIPTION = '仮想マシンを停止する'
    VM_POWEROFF_DESCRIPTION = '仮想マシンを電源OFFにする'

    def __init__(self, session, page: ft.Page, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel

        # controls
        formTitle = FormTitle('仮想マシンの起動/停止', '変更内容')
        formDescription = FormDescription('仮想マシンを起動または停止します。起動・停止に時間を要するサーバは、最大待ち合わせ時間をより大きく設定します。＊は入力/選択が必須の項目です。')
        self.checkChangeStartStopEnabled = ft.Checkbox(
            label='起動/停止の状態を変更する',
            value=self.session.get('job_options')['vm_start_stop_enabled'] if 'vm_start_stop_enabled' in self.session.get('job_options') else True,
            on_change=self.on_change_vm_start_stop_enabled,
            disabled=True,
        )

        self.dropStartStop = ft.Dropdown(
            label='起動または停止(＊)',
            value=VmStartStop.to_friendly(self.session.get('job_options')['vm_start_stop']) if 'vm_start_stop' in self.session.get('job_options') else VmStartStop.STARTUP_FRIENDLY,
            options=[
                ft.dropdown.Option(VmStartStop.STARTUP_FRIENDLY),
                ft.dropdown.Option(VmStartStop.SHUTDOWN_FRIENDLY),
                ft.dropdown.Option(VmStartStop.POWEROFF_FRIENDLY),
            ],
            autofocus=True,
            disabled=(not bool(strtobool(self.session.get('job_options')['vm_start_stop_enabled']))) if 'vm_start_stop_enabled' in self.session.get('job_options') else False,
        )
        self.tfShutdownTimeoutSec = ParameterInputText(
            value=self.session.get('job_options')['shutdown_timeout_sec'] if 'shutdown_timeout_sec' in self.session.get('job_options') else 600,
            label='シャットダウン時の最大待ち合わせ時間(秒)',
            text_align=ft.TextAlign.RIGHT,
            expand=True,
            hint_text='シャットダウンに時間を要するサーバは、この値をより大きく設定して下さい。',
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d{1,4}$", replacement_string=""),
        )
        self.tfToolsWaitTimeoutSec = ParameterInputText(
            value=self.session.get('job_options')['tools_wait_timeout_sec'] if 'tools_wait_timeout_sec' in self.session.get('job_options') else 600,
            label='起動時の最大待ち合わせ時間(秒)',
            text_align=ft.TextAlign.RIGHT,
            expand=True,
            hint_text='起動に時間を要するサーバは、この値をより大きく設定して下さい。',
            input_filter=ft.InputFilter(allow=True, regex_string=r"^\d{1,4}$", replacement_string=""),
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
                self.checkChangeStartStopEnabled,
                self.dropStartStop,
                ft.Row([
                    self.tfShutdownTimeoutSec,
                    self.tfToolsWaitTimeoutSec,
                ]),
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
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=lambda e: self.dropStartStop.focus()
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=lambda e: keyboard_shortcut_manager.dump_key_shortcuts(),
        )
        super().register_key_shortcuts()

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        super().unregister_key_shortcuts()

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
        if str(self.session.get('job_options')['vm_start_stop_enabled']) == 'True':
            confirm_text += '\n起動/停止: ' + VmStartStop.to_friendly(self.session.get('job_options')['vm_start_stop'])
            confirm_text += '\nシャットダウン時の最大待ち合わせ時間(秒): ' + str(self.session.get('job_options')['shutdown_timeout_sec'])
            confirm_text += '\n起動時の最大待ち合わせ時間(秒): ' + str(self.session.get('job_options')['tools_wait_timeout_sec'])
        return confirm_text

    @Logging.func_logger
    def on_change_vm_start_stop_enabled(self, e):
        self.session.get('job_options')['vm_start_stop_enabled'] = str(e.control.value)
        self.dropStartStop.disabled = False if e.control.value else True
        self.tfShutdownTimeoutSec.disabled = False if e.control.value else True
        self.tfToolsWaitTimeoutSec.disabled = False if e.control.value else True
        self.dropStartStop.update()
        self.tfShutdownTimeoutSec.update()
        self.tfToolsWaitTimeoutSec.update()

    @Logging.func_logger
    def on_click_next(self, e):
        self._lock_form_controls()
        self.session.get('job_options')['vm_start_stop_enabled'] = str(self.checkChangeStartStopEnabled.value)
        self.session.get('job_options')['vm_start_stop'] = VmStartStop.to_formal(self.dropStartStop.value)
        self.session.get('job_options')['shutdown_timeout_sec'] = int(self.tfShutdownTimeoutSec.value)
        self.session.get('job_options')['tools_wait_timeout_sec'] = int(self.tfToolsWaitTimeoutSec.value)
        self.session.set('confirm_text', self.generate_confirm_text())
        Logging.info('JOB_OPTIONS: ' + str(self.session.get('job_options')))
        self._unlock_form_controls()
        self.step_change_next(e)
