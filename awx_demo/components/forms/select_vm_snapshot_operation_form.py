import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.utils.logging import Logging


class SelectVmSnapshotOperationForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    RADIO_SNAPSHOT_OPERATION_PADDING_LEFT = 40
    TARGET_VM_SNAPSHOT_ID_NOTOUND = -1
    TARGET_VM_SNAPSHOT_NAME_NOTFOUND = ""

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

        # セッションに値がない場合は、デフォルト値をセット
        if not "snapshot_operation" in self.session.get("job_options"):
            self.session.get("job_options")["snapshot_operation"] = "take_vm_snapshot"
        if not "target_vm_multiple" in self.session.get("job_options"):
            self.session.get("job_options")["target_vm_multiple"] = False

        # controls
        formTitle = FormTitle("スナップショット操作の選択", "仮想マシンのスナップショットに対する操作の指定")
        formDescription = FormDescription(
            "実施したいスナップショット操作を指定して下さい。＊は入力/選択が必須の項目です。"
        )

        # スナップショット操作の選択
        self.textVmSnapshotOperation = ft.Text(
            value="実施する操作（＊）",
            size=14,
            weight=ft.FontWeight.BOLD,
        )
        self.radioSnapshotOperation = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Radio(
                        value="take_vm_snapshot",
                        label="スナップショットの取得",
                        tooltip="仮想マシンのスナップショットを取得します。",
                    ),
                    ft.Radio(
                        value="revert_vm_snapshot",
                        label="スナップショットの切り戻し",
                        tooltip="仮想マシンを指定したスナップショットの状態に切り戻します。",
                    ),
                    ft.Radio(
                        value="remove_vm_snapshot",
                        label="スナップショットの削除",
                        tooltip="仮想マシンの指定したスナップショットを削除します。",
                    ),
                ],
            ),
            on_change=self.on_change_radio_snapshot_operation,
            value=self.session.get("job_options")["snapshot_operation"],
        )
        self.checkTargetVmMultiple = ft.Checkbox(
            label="複数の仮想マシンを対象とします。\n切り戻し・削除の場合、事前に各仮想マシンに同名のスナップショットを作成する必要があります。",
            value=self.session.get("job_options")["target_vm_multiple"],
            on_change=self.on_change_check_target_vm_multiple,
        )

        self.btnNext = ft.FilledButton(
            "次へ",
            tooltip="次へ (Shift+Alt+N)",
            on_click=self.on_click_next,
        )
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
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.textVmSnapshotOperation,
                            self.radioSnapshotOperation,
                            self.checkTargetVmMultiple,
                        ],
                    ),
                    padding=ft.padding.only(left=self.RADIO_SNAPSHOT_OPERATION_PADDING_LEFT),
                ),
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

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
            func=lambda e: self.dropVcenter.focus(),
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(key="Z", shift=True, ctrl=False, alt=True, meta=False),
            func=lambda e: keyboard_shortcut_manager.dump_key_shortcuts(),
        )
        super().register_key_shortcuts()

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        if self.page:
            keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
            # autofocus=Trueである、最初のコントロールにフォーカスを移動する
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
            )
            # ログへのキーボードショートカット一覧出力
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(key="Z", shift=True, ctrl=False, alt=True, meta=False),
            )
            super().unregister_key_shortcuts()

    @Logging.func_logger
    def on_change_radio_snapshot_operation(self, e):
        # スナップショット操作を変更した場合は、スナップショットIDとスナップショット名をリセット
        if self.session.get("job_options")["snapshot_operation"] != e.control.value:
            self.session.get("job_options")["target_vm_snapshot_id"] = self.TARGET_VM_SNAPSHOT_ID_NOTOUND
            self.session.get("job_options")["target_vm_snapshot_name"] = self.TARGET_VM_SNAPSHOT_NAME_NOTFOUND

        self.session.get("job_options")["snapshot_operation"] = e.control.value

    @Logging.func_logger
    def on_change_check_target_vm_multiple(self, e):
        self.session.get("job_options")["target_vm_multiple"] = e.control.value

    @Logging.func_logger
    def on_click_next(self, e):
        self._lock_form_controls()
        self.step_change_next(e)
        self._unlock_form_controls()
