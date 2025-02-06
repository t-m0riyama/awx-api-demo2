import os
from distutils.util import strtobool

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.utils.logging import Logging


class SetVmCpuForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_CPUS_DEFAULT = '1,2,4,6,8'

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
        formTitle = FormTitle('CPUの割り当て変更', '変更内容')
        formDescription = FormDescription('仮想マシンに割り当てるCPUコア数を変更します。＊は入力/選択が必須の項目です。')
        self.checkChangeVmCpuEnabled = ft.Checkbox(
            label='CPUコア数を変更する',
            value=self.session.get('job_options')['change_vm_cpu_enabled'] if 'change_vm_cpu_enabled' in self.session.get('job_options') else True,
            autofocus=True,
            on_change=self.on_change_vm_cpu_enabled,
        )

        # 選択可能なCPUコア数の決定
        vm_cpus = os.getenv('RMX_VM_CPUS', self.VM_CPUS_DEFAULT).strip('"').strip('\'')
        vm_cpu_options = []
        for vm_cpu_option in vm_cpus.split(","):
            vm_cpu_options.append(ft.dropdown.Option(vm_cpu_option.strip()))

        self.dropCpus = ft.Dropdown(
            label='CPUコア数(＊)',
            value=self.session.get('job_options')['vcpus'] if 'vcpus' in self.session.get('job_options') else '2',
            options=vm_cpu_options,
            autofocus=True,
            disabled=(not bool(strtobool(self.session.get('job_options')['change_vm_cpu_enabled']))) if 'change_vm_cpu_enabled' in self.session.get('job_options') else False,
        )
        self.btnNext = ft.FilledButton(
            '次へ', tooltip='次へ (Shift+Alt+N)', on_click=self.on_click_next)
        self.btnPrev = ft.ElevatedButton(
            '戻る', tooltip='戻る (Control+Shift+P)', on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            'キャンセル', tooltip='キャンセル (Control+Shift+X)', on_click=self.on_click_cancel)

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

        self.controls = ft.Container(
            ft.SelectionArea(
                content=ft.Column(
                    [
                        header,
                        body,
                        ft.Divider(),
                        footer,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ),
            width=self.content_width,
            height=self.content_height,
            padding=30,
        )
        super().__init__(self.controls)

    # @Logging.func_logger
    # def register_key_shortcuts(self):
    #     keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
    #     # autofocus=Trueである、最初のコントロールにフォーカスを移動する
    #     keyboard_shortcut_manager.register_key_shortcut(
    #         key_set=keyboard_shortcut_manager.create_key_set(
    #             key="F", shift=True, ctrl=True, alt=False, meta=False
    #         ),
    #         func=lambda e: self.checkChangeVmCpuEnabled.focus() # fletのcheckboxにfocus()が未実装のため見送り
    #     )
    #     # ログへのキーボードショートカット一覧出力
    #     keyboard_shortcut_manager.register_key_shortcut(
    #         key_set=keyboard_shortcut_manager.create_key_set(
    #             key="Z", shift=True, ctrl=True, alt=False, meta=False,
    #         ),
    #         func=lambda e: keyboard_shortcut_manager.dump_key_shortcuts(),
    #     )
    #     super().register_key_shortcuts()

    # @Logging.func_logger
    # def unregister_key_shortcuts(self):
    #     keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
    #     # autofocus=Trueである、最初のコントロールにフォーカスを移動する
    #     keyboard_shortcut_manager.unregister_key_shortcut(
    #         key_set=keyboard_shortcut_manager.create_key_set(
    #             key="F", shift=True, ctrl=True, alt=False, meta=False
    #         ),
    #     )
    #     # ログへのキーボードショートカット一覧出力
    #     keyboard_shortcut_manager.unregister_key_shortcut(
    #         key_set=keyboard_shortcut_manager.create_key_set(
    #             key="Z", shift=True, ctrl=True, alt=False, meta=False
    #         ),
    #     )
    #     super().unregister_key_shortcuts()

    @Logging.func_logger
    def on_change_vm_cpu_enabled(self, e):
        self.session.get('job_options')['change_vm_cpu_enabled'] = str(e.control.value)
        self.dropCpus.disabled = False if e.control.value else True
        self.dropCpus.update()

    @Logging.func_logger
    def on_click_next(self, e):
        self._lock_form_controls()
        self.session.get('job_options')['change_vm_cpu_enabled'] = str(self.checkChangeVmCpuEnabled.value)
        self.session.get('job_options')['vcpus'] = int(self.dropCpus.value)
        self._unlock_form_controls()
        self.step_change_next(e)
