import flet as ft

from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.forms.dashboard_tab.in_progress_tab_form import InProgressTabForm
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.utils.logging import Logging


class DashboardForm(ft.Card):

    # const
    CONTENT_HEIGHT = 640
    CONTENT_WIDTH = 1000
    BODY_HEIGHT = 590
    DATA_ROW_MAX = 20
    TAB_LABEL_FONT_SIZE = 12
    DEFAULT_SORT_TARGET_COLUMN = "時刻"
    DEFAULT_SORT_COLUMN_INDEX = 1
    DEFAULT_SORT_ASCENDING = False
    FORM_TITLE = "ダッシュボード"
    FILTERED_IAAS_USERS_DEFAULT = "root,admin,awxcli"

    def __init__(self, session, page: ft.Page):
        self.session = session
        self.page = page
        self.content_height = self.CONTENT_HEIGHT
        self.content_width = self.CONTENT_WIDTH
        self.body_height = self.BODY_HEIGHT
        self.data_row_offset = 0
        self.session.set("sort_target_column", self.DEFAULT_SORT_TARGET_COLUMN)
        self.tab_content_height = self.content_height
        self.tab_content_width = self.content_width
        self.tab_body_height = self.body_height

        formTitle = FormTitle(self.FORM_TITLE, None)
        self.formInProgress = InProgressTabForm(
            session=self.session,
            page=self.page,
            height=self.tab_content_height,
            width=self.tab_content_width,
            body_height=self.tab_body_height,
        )
        self.tabRequest = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    tab_content=ft.Text("対応中", tooltip="対応中 (Shift+Alt+G)"),
                    content=self.formInProgress,
                    # height=self.tab_body_height,
                ),
            ],
            label_text_style=ft.TextStyle(size=self.TAB_LABEL_FONT_SIZE),
            scrollable=True,
            expand=True,
        )

        # Content
        header = ft.Container(
            formTitle,
        )
        body = ft.Column(
            [
                self.tabRequest,
            ],
            height=self.body_height,
        )

        self.controls = ft.Container(
            ft.ResponsiveRow(
                [
                    ft.Column(
                        col={"sm": 12},
                        controls=[
                            header,
                            body,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ]
            ),
        )
        self.register_key_shortcuts()
        super().__init__(content=self.controls, expand=True)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
            func=lambda e: self.tabRequest.focus(),
        )

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        if self.page:
            keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
            # autofocus=Trueである、最初のコントロールにフォーカスを移動する
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
            )

    def refresh(self, e=None):
        self.formInProgress.refresh()

    @Logging.func_logger
    def _lock_form_controls(self):
        # クリック連打対策
        self.controls.disabled = True
        self.controls.update()

    @Logging.func_logger
    def _unlock_form_controls(self):
        # クリック連打対策解除
        self.controls.disabled = False
        self.controls.update()
