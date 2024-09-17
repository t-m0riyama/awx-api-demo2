import flet as ft

from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.event_manager import EventManager
from awx_demo.utils.logging import Logging


class AppHeader(ft.Row):

    def __init__(self, session, page: ft.Page, app_title):
        super().__init__()
        self.session = session
        self.page = page
        self.app_title = app_title
        self.toggle_dark_light_icon = ft.IconButton(
            icon="light_mode",
            selected_icon="dark_mode",
            tooltip="ライトモード/ダークモードの切り替え",
            on_click=self.toggle_icon,
        )
        role_friendly = UserRole.to_friendly(self.session.get("user_role"))
        self.appbar_items = [
            ft.PopupMenuItem(
                text=(self.session.get("awx_loginid") + " (" + role_friendly + ")")
            ),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(text="ログアウト", on_click=self.logout_clicked),
            # ft.PopupMenuItem(text='設定'),
        ]
        # appbarフィールドの設定
        self.page.appbar = ft.AppBar(
            leading=ft.Icon(ft.icons.HANDYMAN_OUTLINED),
            leading_width=100,
            title=ft.Text(
                value=self.app_title,
                color=ft.colors.PRIMARY,
                size=28,
                text_align=ft.TextAlign.CENTER,
            ),
            center_title=False,
            toolbar_height=46,
            bgcolor=ft.colors.SURFACE_VARIANT,
            actions=[
                ft.Container(
                    content=ft.Row(
                        [
                            self.toggle_dark_light_icon,
                            ft.PopupMenuButton(
                                icon=ft.icons.ACCOUNT_CIRCLE,
                                items=self.appbar_items,
                                tooltip="アカウント設定",
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    margin=ft.margin.only(left=50, right=25),
                )
            ],
        )

    @Logging.func_logger
    def toggle_icon(self, e):
        self.page.theme_mode = "dark" if self.page.theme_mode == "light" else "light"
        self.toggle_dark_light_icon.selected = not self.toggle_dark_light_icon.selected
        self.page.update()

    @Logging.func_logger
    def logout_clicked(self, e):
        activity_spec = ActivityHelper.ActivitySpec(
            user=self.session.get("awx_loginid"),
            request_id="",
            event_type=EventType.LOGOUT,
            status=EventStatus.SUCCEED,
            summary="ログアウトに成功しました。",
            detail="",
        )
        EventManager.emit_event(
            activity_spec=activity_spec,
            notification_specs=[],
        )
        SessionHelper.clean_session(self.session)
        self.page.go("/login")
