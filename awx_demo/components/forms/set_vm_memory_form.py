import os
from distutils.util import strtobool

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.utils.logging import Logging


class SetVmMemoryForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_MEMORY_SIZES_GB_DEFAULT = "4,8,12,16,24,32"

    def __init__(
        self,
        session,
        page: ft.Page,
        height=CONTENT_HEIGHT,
        width=CONTENT_WIDTH,
        body_height=BODY_HEIGHT,
        step_change_next=None,
        step_change_previous=None,
        step_change_cancel=None,
    ):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel

        # controls
        formTitle = FormTitle("メモリの割り当て変更", "変更内容")
        formDescription = FormDescription(
            "仮想マシンに割り当てるメモリ容量を変更します。＊は入力/選択が必須の項目です。"
        )

        self.checkChangeVmMemoryEnabled = ft.Checkbox(
            label="メモリ容量を変更する",
            value=(
                self.session.get("job_options")["change_vm_memory_enabled"]
                if "change_vm_memory_enabled" in self.session.get("job_options")
                else True
            ),
            autofocus=True,
            on_change=self.on_change_vm_memory_enabled,
        )

        # 選択可能なメモリ容量の決定
        vm_memory_sizes = os.getenv("RMX_VM_MEMORY_SIZES_GB", self.VM_MEMORY_SIZES_GB_DEFAULT).strip('"').strip("'")
        vm_memory_sizes_array = [x.strip() for x in vm_memory_sizes.split(",")]
        vm_memory_options = []
        for vm_memory_option in vm_memory_sizes_array:
            vm_memory_options.append(ft.dropdown.Option(vm_memory_option))

        # 設定変更前のメモリ容量が選択可能なメモリ容量に含まれていない場合は、選択可能なメモリ容量に追加
        if self.session.contains_key("memory_gb_default"):
            if str(self.session.get("memory_gb_default")) not in vm_memory_sizes_array:
                vm_memory_options.append(ft.dropdown.Option(str(self.session.get("memory_gb_default"))))

        # メモリ容量のデフォルト値を決定
        if "memory_gb" in self.session.get("job_options"):
            vm_memory_gb_default = str(self.session.get("job_options")["memory_gb"])
        elif self.session.contains_key("memory_gb_default"):
            vm_memory_gb_default = str(self.session.get("memory_gb_default"))
        else:
            vm_memory_gb_default = "8"

        self.dropMemorySize = ft.Dropdown(
            label="メモリ容量(GB)(＊)",
            value=vm_memory_gb_default,
            options=vm_memory_options,
            autofocus=True,
            disabled=(
                (not bool(strtobool(self.session.get("job_options")["change_vm_memory_enabled"])))
                if "change_vm_memory_enabled" in self.session.get("job_options")
                else False
            ),
            expand=True,
        )
        self.btnNext = ft.FilledButton("次へ", tooltip="次へ (Shift+Alt+N)", on_click=self.on_click_next)
        self.btnPrev = ft.ElevatedButton("戻る", tooltip="戻る (Shift+Alt+P)", on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            "キャンセル",
            tooltip="キャンセル (Shift+Alt+X)",
            on_click=self.on_click_cancel,
        )

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
                self.checkChangeVmMemoryEnabled,
                self.dropMemorySize,
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
    #             key="F", shift=True, ctrl=False, alt=True, meta=False
    #         ),
    #         func=lambda e: self.checkChangeVmMemoryEnabled.focus() # fletのcheckboxにfocus()が未実装のため見送り
    #     )

    # @Logging.func_logger
    # def unregister_key_shortcuts(self):
    #     if self.page:
    #         keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
    #         # autofocus=Trueである、最初のコントロールにフォーカスを移動する
    #         keyboard_shortcut_manager.unregister_key_shortcut(
    #             key_set=keyboard_shortcut_manager.create_key_set(
    #                 key="F", shift=True, ctrl=False, alt=True, meta=False
    #             ),
    #         )

    @Logging.func_logger
    def generate_confirm_text(self):
        confirm_text = "== 基本情報 ====================="
        confirm_text += "\n依頼者(アカウント): " + self.session.get("awx_loginid")
        confirm_text += "\n依頼内容: " + (
            self.session.get("request_text")
            if self.session.contains_key("request_text") and self.session.get("request_text") != ""
            else "(未指定)"
        )
        confirm_text += "\n依頼区分: " + self.session.get("request_category")
        confirm_text += "\n申請項目: " + self.session.get("request_operation")
        request_deadline = (
            self.session.get("request_deadline").strftime("%Y/%m/%d")
            if self.session.contains_key("request_deadline")
            else "(未指定)"
        )
        confirm_text += "\nリリース希望日: " + request_deadline
        confirm_text += "\n\n== 詳細情報 ====================="
        confirm_text += "\nvCenter: " + self.session.get("job_options")["vsphere_vcenter"]
        confirm_text += "\n仮想マシン: " + self.session.get("job_options")["target_vms"]
        if str(self.session.get("job_options")["change_vm_cpu_enabled"]) == "True":
            confirm_text += "\nCPUコア数: " + str(self.session.get("job_options")["vcpus"])
        if str(self.session.get("job_options")["change_vm_memory_enabled"]) == "True":
            confirm_text += "\nメモリ容量(GB): " + str(self.session.get("job_options")["memory_gb"])
        return confirm_text

    @Logging.func_logger
    def on_change_vm_memory_enabled(self, e):
        self.session.get("job_options")["change_vm_memory_enabled"] = str(e.control.value)
        self.dropMemorySize.disabled = False if e.control.value else True
        self.dropMemorySize.update()

    @Logging.func_logger
    def on_click_next(self, e):
        self._lock_form_controls()
        self.session.get("job_options")["change_vm_memory_enabled"] = str(self.checkChangeVmMemoryEnabled.value)
        self.session.get("job_options")["memory_gb"] = int(self.dropMemorySize.value)
        self.session.set("confirm_text", self.generate_confirm_text())
        Logging.info("JOB_OPTIONS: " + str(self.session.get("job_options")))
        self._unlock_form_controls()
        self.step_change_next(e)
