import flet as ft

from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
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
            tooltip="ライトモード/ダークモードの切り替え (Cotrol+Shift+T)",
            on_click=self.toggle_thema_mode,
        )
        role_friendly = UserRole.to_friendly(self.session.get("user_role"))
        self.appbar_items = [
            ft.PopupMenuItem(
                text=(self.session.get("awx_loginid") + " [" + role_friendly + "]")
            ),
            ft.PopupMenuItem(),
            ft.PopupMenuItem(
                content=ft.Text(
                    "ログアウト (Cotrol+Shift+Q)"
                ),
                on_click=self.logout_clicked
            ),
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
        self.register_key_shortcuts()

    @Logging.func_logger
    def register_key_shortcuts(self):
        keybord_shortcut_manager = KeyboardShortcutManager(self.page)
        # ダークモード/ライトモードのテーマ切り替え
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="T", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=self.toggle_thema_mode,
        )
        # ログアウト
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Q", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=self.logout_clicked,
        )
        # ログへのセッションダンプ
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="V", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=lambda e, session=self.session: SessionHelper.dump_session(session),
        )
        # ログへのキーボードショートカット一覧出力
        keybord_shortcut_manager.register_key_shortcut(
            key_set=keybord_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=lambda e: keybord_shortcut_manager.dump_key_shortcuts(),
        )

    @Logging.func_logger
    def toggle_thema_mode(self, e):
        self.page.theme_mode = "dark" if self.page.theme_mode == "light" else "light"
        self.toggle_dark_light_icon.selected = not self.toggle_dark_light_icon.selected
        self.page.update()

    @Logging.func_logger
    def logout_clicked(self, e):
        activity_spec = ActivityHelper.ActivitySpec(
            user=self.session.get("awx_loginid"),
            request_id="",
            activity_type=EventType.LOGOUT,
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
