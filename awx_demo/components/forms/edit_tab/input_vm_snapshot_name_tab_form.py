import datetime
import flet as ft

from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.utils.logging import Logging


class InputVmSnapshotNameTabForm(ft.Card):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_SNAPSHOT_NAME_LENGTH_MAX = 60
    VM_SNAPSHOT_DESCRIPTION_LENGTH_MAX = 120

    def __init__(self, session, page, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height

        # controls
        default_vm_snapshot_name = f"Snapshot {datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}"
        self.tfVmSnapshotName = ParameterInputText(
            label="スナップショット名(＊)",
            value=(
                self.session.get("job_options")["target_vm_snapshot_name"]
                if "target_vm_snapshot_name" in self.session.get("job_options")
                else default_vm_snapshot_name
            ),
            max_length=self.VM_SNAPSHOT_NAME_LENGTH_MAX,
            show_counter=True,
            on_change=self.on_change_vm_snapshot_name,
        )
        self.tfVmSnapshotDescription = ParameterInputText(
            label="説明",
            value=(
                self.session.get("job_options")["target_vm_snapshot_description"]
                if "target_vm_snapshot_description" in self.session.get("job_options")
                else ""
            ),
            max_length=self.VM_SNAPSHOT_DESCRIPTION_LENGTH_MAX,
            show_counter=True,
            on_change=self.on_change_vm_snapshot_description,
        )

        # Content
        body = ft.Column(
            [
                ft.ResponsiveRow([self.tfVmSnapshotName, self.tfVmSnapshotDescription]),
            ],
            height=self.body_height,
        )

        self.controls = ft.Container(
            ft.SelectionArea(
                content=ft.Column(
                    [
                        body,
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
    #         key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
    #         func=lambda e: self.panelListVms.focus(),
    #     )
    #     # ログへのキーボードショートカット一覧出力
    #     keyboard_shortcut_manager.register_key_shortcut(
    #         key_set=keyboard_shortcut_manager.create_key_set(
    #             key="Z",
    #             shift=True,
    #             ctrl=False,
    #             alt=True,
    #             meta=False,
    #         ),
    #         func=lambda e: keyboard_shortcut_manager.dump_key_shortcuts(),
    #     )
    #     super().register_key_shortcuts()

    # @Logging.func_logger
    # def unregister_key_shortcuts(self):
    #     if self.page:
    #         keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
    #         # autofocus=Trueである、最初のコントロールにフォーカスを移動する
    #         keyboard_shortcut_manager.unregister_key_shortcut(
    #             key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
    #         )
    #         # ログへのキーボードショートカット一覧出力
    #         keyboard_shortcut_manager.unregister_key_shortcut(
    #             key_set=keyboard_shortcut_manager.create_key_set(key="Z", shift=True, ctrl=False, alt=True, meta=False),
    #         )
    #         super().unregister_key_shortcuts()

    @Logging.func_logger
    def refresh_vm_snapshots_available(self):
        # vCenterや仮想マシンが変更された際、スナップショットのリストを更新する必要はないため、処理を行わない
        pass

    @Logging.func_logger
    def on_change_vm_snapshot_name(self, e):
        self.session.get("job_options")["target_vm_snapshot_name"] = e.control.value

    @Logging.func_logger
    def on_change_vm_snapshot_description(self, e):
        self.session.get("job_options")["target_vm_snapshot_description"] = e.control.value
