import abc
import os

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.forms.helper.activity_row_helper import ActivityRowData, ActivityRowHelper
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.event_helper import EventType
from awx_demo.utils.logging import Logging


class BaseActivityListForm(ft.Card, metaclass=abc.ABCMeta):

    # const
    CONTENT_HEIGHT = 640
    CONTENT_WIDTH = 1000
    BODY_HEIGHT = 540
    DATA_ROW_MAX = 20
    DEFAULT_SORT_TARGET_COLUMN = "時刻"
    DEFAULT_SORT_COLUMN_INDEX = 1
    DEFAULT_SORT_ASCENDING = False
    FORM_TITLE = "操作履歴"
    FILTERED_IAAS_USERS_DEFAULT = "root,admin,awxcli"

    def __init__(self, session, page: ft.Page):
        self.session = session
        self.page = page
        self.data_row_offset = 0
        self.session.set("sort_target_column", self.DEFAULT_SORT_TARGET_COLUMN)
        formTitle = FormTitle(self.FORM_TITLE, None)
        self.dtActivities = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("時刻"), on_sort=self.on_click_heading_column),
                ft.DataColumn(
                    ft.Text("ユーザ名"), on_sort=self.on_click_heading_column
                ),
                ft.DataColumn(
                    ft.Text("操作種別"), on_sort=self.on_click_heading_column
                ),
                ft.DataColumn(ft.Text("依頼ID"), on_sort=self.on_click_heading_column),
                ft.DataColumn(ft.Text("概要"), on_sort=self.on_click_heading_column),
            ],
            rows=[],
            show_checkbox_column=False,
            show_bottom_border=True,
            border=ft.border.all(2, ft.colors.SURFACE_VARIANT),
            border_radius=10,
            divider_thickness=1,
            heading_row_color=ft.colors.SURFACE_VARIANT,
            heading_row_height=40,
            data_row_max_height=60,
            column_spacing=15,
            sort_column_index=self.DEFAULT_SORT_COLUMN_INDEX,
            sort_ascending=self.DEFAULT_SORT_ASCENDING,
            # expand=True,
            # data_row_color={"hovered": "0x30FF0000"},
        )

        # self.session.set('sort_target_column', self.DEFAULT_SORT_TARGET_COLUMN)
        activities_data = ActivityRowHelper.query_activity_all(self)
        self.dtActivities.rows = []
        for activity_data in activities_data:
            activity_row_data = ActivityRowData(
                user=activity_data.user,
                created=activity_data.created.strftime("%Y/%m/%d %H:%M"),
                activity_type=EventType.to_friendly(activity_data.activity_type),
                status=activity_data.status,
                summary=activity_data.summary,
                detail=activity_data.detail,
            )
            self.dtActivities.rows.append(
                ActivityRowHelper.generate_activity_row(
                    self,
                    activity_data.request_id,
                    activity_row_data,
                )
            )
        self.rowRequests = ft.ResponsiveRow(
            [
                ft.Column(
                    col={"sm": 12},
                    controls=[self.dtActivities],
                    scroll=ft.ScrollMode.AUTO,
                )
            ],
            expand=1,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

        iaas_user_options = []
        if self.session.get("user_role") != UserRole.USER_ROLE:
            filtered_users = os.getenv("RMX_FILTERED_IAAS_USERS", self.FILTERED_IAAS_USERS_DEFAULT).strip('"').strip('\'').split(",")
            filtered_users = list(map(lambda s: s.strip(), filtered_users))
            iaas_users = AWXApiHelper.get_users(
                self.session.get("awx_url"),
                self.session.get("awx_loginid"),
                self.session.get("awx_password"),
                filtered_users,
            )
        else:
            iaas_users = []

        # iaas_users = []  # for DEBUG
        iaas_users.insert(0, {"username": "すべてのユーザ"})
        for iaas_user in iaas_users:
            iaas_user_options.append(ft.dropdown.Option(iaas_user["username"]))

        # 申請者ロールの場合は、変更できないようにする
        user_change_disabled = (
            True if self.session.get("user_role") == UserRole.USER_ROLE else False
        )
        self.dropUser = ft.Dropdown(
            label="ユーザ",
            value=(
                self.session.get("activity_user")
                if self.session.contains_key("activity_user")
                else "すべてのユーザ"
            ),
            options=iaas_user_options,
            hint_text="操作を実行したアカウント",
            on_change=self.on_change_filter_activity_user,
            # width=150,
            expand=True,
            dense=True,
            disabled=user_change_disabled,
        )
        self.dropActivityType = ft.Dropdown(
            label="操作種別",
            value=(
                self.session.get("activity_type")
                if self.session.contains_key("activity_type")
                else "すべての操作"
            ),
            options=[
                ft.dropdown.Option("すべての操作"),
                ft.dropdown.Option(EventType.LOGIN_FRIENDLY),
                ft.dropdown.Option(EventType.LOGOUT_FRIENDLY),
                ft.dropdown.Option(EventType.REQUEST_SENT_FRIENDLY),
                ft.dropdown.Option(EventType.REQUEST_CHANGED_FRIENDLY),
                ft.dropdown.Option(EventType.REQUEST_STATUS_CHANGED_FRIENDLY),
                ft.dropdown.Option(EventType.REQUEST_IAAS_USER_ASSIGNED_FRIENDLY),
                ft.dropdown.Option(EventType.REQUEST_EXECUTE_STARTED_FRIENDLY),
                ft.dropdown.Option(EventType.REQUEST_EXECUTE_COMPLETED_FRIENDLY),
                ft.dropdown.Option(EventType.REQUEST_DELETED_FRIENDLY),
                ft.dropdown.Option(EventType.GLOBAL_SETTING_CHANGED_FRIENDLY),
            ],
            hint_text="操作種別を指定します。",
            on_change=self.on_change_filter_activity_type,
            # width=200,
            expand=True,
            dense=True,
        )

        self.tfSearchSummary = ParameterInputText(
            label="概要を検索",
            # width=220,
            expand=True,
            on_submit=self.on_click_search_summary,
        )
        self.btnSearchSummary = ft.IconButton(
            icon=ft.icons.SEARCH,
            icon_color=ft.colors.ON_SURFACE_VARIANT,
            on_click=self.on_click_search_summary,
            autofocus=True,
            tooltip="検索 (Control+Enter)",
        )
        self.btnReloadRequestList = ft.IconButton(
            icon=ft.icons.SYNC,
            icon_color=ft.colors.ON_SURFACE_VARIANT,
            on_click=lambda e: self.refresh(),
            autofocus=True,
            tooltip="操作履歴一覧の再読み込み (Control+R)",
        )
        range_min, range_max, request_data_count = ActivityRowHelper.get_page_range(
            self
        )
        self.textRequestsRange = ft.Text(
            "{}-{} / {}".format(range_min, range_max, request_data_count)
        )
        self.btnPreviousPage = ft.IconButton(
            tooltip="前へ (Control+Shift+<)",
            icon=ft.icons.ARROW_LEFT,
            icon_color=ft.colors.ON_INVERSE_SURFACE,
            on_click=self.on_click_previous_page,
            disabled=True,
        )
        self.btnNextPage = ft.IconButton(
            tooltip="次へ (Control+Shift+>)",
            icon=ft.icons.ARROW_RIGHT,
            icon_color=ft.colors.ON_SURFACE_VARIANT,
            on_click=self.on_click_next_page,
        )

        # Content
        header = ft.Container(
            formTitle,
        )
        body = ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        ft.Row(
                            col={"sm": 6},
                            controls=[
                                self.dropUser,
                                self.dropActivityType,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Row(
                            col={"sm": 3},
                            controls=[
                                self.tfSearchSummary,
                                self.btnSearchSummary,
                                self.btnReloadRequestList,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            col={"sm": 3},
                            controls=[
                                self.btnPreviousPage,
                                self.textRequestsRange,
                                self.btnNextPage,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.rowRequests,
            ],
            height=self.BODY_HEIGHT,
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
            height=self.CONTENT_HEIGHT,
            # padding=ft.padding.all(0),
        )
        self.register_key_shortcuts()
        super().__init__(self.controls)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keybord_shortcut_manager = KeyboardShortcutManager(self.page)
        # 操作履歴一覧のページ送り / 次のページへ
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key=">", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=self.on_click_next_page,
        )
        # 操作履歴一覧のページ送り / 前のページへ
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="<", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=self.on_click_previous_page,
        )
        # 操作履歴一覧のページ送り / 次のページへ
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Arrow Right", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=self.on_click_next_page,
        )
        # 操作履歴一覧のページ送り / 前のページへ
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Arrow Left", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=self.on_click_previous_page,
        )

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        keybord_shortcut_manager = KeyboardShortcutManager(self.page)
        # 操作履歴一覧のページ送り / 次のページへ
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key=">", shift=True, ctrl=True, alt=False, meta=False,
            ),
        )
        # 操作履歴一覧のページ送り / 前のページへ
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="<", shift=True, ctrl=True, alt=False, meta=False,
            ),
        )
        # 操作履歴一覧のページ送り / 次のページへ
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Arrow Right", shift=True, ctrl=True, alt=False, meta=False,
            ),
        )
        # 操作履歴一覧のページ送り / 前のページへ
        keybord_shortcut_manager.unregister_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Arrow Left", shift=True, ctrl=True, alt=False, meta=False,
            ),
        )

    @abc.abstractmethod
    def get_query_filters(self):
        pass

    def refresh(self, e=None):
        ActivityRowHelper.refresh_data_rows(self)
        ActivityRowHelper.refresh_page_indicator(self)

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
        request_data_count = ActivityRowHelper.count_activity_all(self)
        if (self.data_row_offset + 1) < request_data_count:
            self.data_row_offset += self.DATA_ROW_MAX
            self.refresh()

    @Logging.func_logger
    def on_click_previous_page(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
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
