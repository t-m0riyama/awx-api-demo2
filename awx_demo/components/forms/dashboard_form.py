import os

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.forms.dashboard_tab.in_progress_tab_form import InProgressTabForm
from awx_demo.components.forms.helper.activity_row_helper import ActivityRowData, ActivityRowHelper
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.event_helper import EventType
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
            session = self.session,
            page = self.page,
            height = self.tab_content_height,
            width = self.tab_content_width,
            body_height = self.tab_body_height,
        )
        self.tabRequest = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    tab_content=ft.Text('対応中', tooltip='対応中 (Shift+Alt+G)'),
                    content=ft.SelectionArea(content=self.formInProgress),
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
            # width=self.CONTENT_WIDTH,
            # height=self.CONTENT_HEIGHT,
            # padding=ft.padding.all(0),
        )
        self.register_key_shortcuts()
        super().__init__(content=self.controls, expand=True)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=lambda e: self.dropUser.focus()
        )
        # 概要に含まれる文字の検索を実行
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Enter", shift=False, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_search_summary,
        )
        # 操作履歴一覧の再読み込み
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="R", shift=False, ctrl=True, alt=True, meta=False,
            ),
            func=lambda e: self.refresh(),
        )
        # 操作履歴一覧のページ送り / 次のページへ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Arrow Right", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=self.on_click_next_page,
        )
        # 操作履歴一覧のページ送り / 前のページへ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Arrow Left", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=self.on_click_previous_page,
        )

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        if self.page:
            keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
            # autofocus=Trueである、最初のコントロールにフォーカスを移動する
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="F", shift=True, ctrl=False, alt=True, meta=False
                ),
            )
            # 概要に含まれる文字の検索を実行
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="Enter", shift=False, ctrl=True, alt=False, meta=False
                ),
            )
            # 操作履歴一覧の再読み込み
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="R", shift=False, ctrl=True, alt=True, meta=False
                ),
            )
            # 操作履歴一覧のページ送り / 次のページへ
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="Arrow Right", shift=True, ctrl=False, alt=True, meta=False
                ),
            )
            # 操作履歴一覧のページ送り / 前のページへ
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="Arrow Left", shift=True, ctrl=False, alt=True, meta=False
                ),
            )

    def refresh(self, e=None):
        # ActivityRowHelper.refresh_data_rows(self)
        # ActivityRowHelper.refresh_page_indicator(self)
        pass

    @Logging.func_logger
    def on_request_edit_open(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self.session.set("request_id", e.control.content.value)
        # TODO: アクティビティの詳細をダイアログで表示する場合は別途実装する
        # self.open_edit_request_dialog()

    @Logging.func_logger
    def on_change_filter_activity_user(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self.session.set("filter_activity_user", e.control.value)
        ActivityRowHelper.query_activity_all(self)
        self.refresh()

    @Logging.func_logger
    def on_change_filter_activity_type(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self.session.set("filter_activity_type", e.control.value)
        ActivityRowHelper.query_activity_all(self)
        self.refresh()

    @Logging.func_logger
    def on_click_heading_column(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        ActivityRowHelper.sort_column(self, self.session, e.control.label.value)

    @Logging.func_logger
    def on_click_next_page(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        if self.btnNextPage.disabled:
            self._unlock_form_controls()
            return
        request_data_count = ActivityRowHelper.count_activity_all(self)
        if (self.data_row_offset + 1) < request_data_count:
            self.data_row_offset += self.DATA_ROW_MAX
            self.refresh()

    @Logging.func_logger
    def on_click_previous_page(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        if self.btnPreviousPage.disabled:
            self._unlock_form_controls()
            return
        if (self.data_row_offset + 1) > self.DATA_ROW_MAX:
            self.data_row_offset -= self.DATA_ROW_MAX
            self.refresh()

    @Logging.func_logger
    def on_click_search_summary(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self.data_row_offset = 0
        self.session.set("request_text_search_string", self.tfSearchSummary.value)
        self.refresh()

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
