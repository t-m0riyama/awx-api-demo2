from functools import partial

import flet as ft

from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.logging import Logging


class Sidebar(ft.Container):

    # const
    CONTENT_HEIGHT = 640
    CONTENT_WIDTH = 140
    RAIL_MAX_WIDTH = 130
    RAIL_MIN_WIDTH = 0
    MAIN_RAIL_HEIGHT = 380
    OPTION_RAIL_HEIGHT = 120
    ICON_SIZE = 28

    def __init__(self, session, page: ft.Page, default_selected_index=0):
        self.session = session
        self.page = page
        self.nav_rail_visible = True
        if self.session.get('user_role') == UserRole.USER_ROLE:
            self.main_nav_rail_items = [
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.FIBER_NEW, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.FIBER_NEW_OUTLINED, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "最新",
                        tooltip="最新の申請 (Cotrol+Shift+L)",
                    )
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.WARNING_AMBER, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.WARNING_AMBER_OUTLINED, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "リリース希望日",
                        tooltip="リリース希望日 (Cotrol+Shift+D)",
                    )
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.LIST, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.LIST_OUTLINED, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "全て",
                        tooltip="全て (Cotrol+Shift+A)",
                    )
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.CHECK_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(ft.Icons.CHECK, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "完了",
                        tooltip="完了 (Cotrol+Shift+E)",
                    )
                ),
            ]
        else:
            self.main_nav_rail_items = [
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.FIBER_NEW, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.FIBER_NEW_OUTLINED, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "最新",
                        tooltip="最新の申請 (Cotrol+Shift+L)",
                    )
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.WARNING_AMBER, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.WARNING_AMBER_OUTLINED, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "リリース希望日",
                        tooltip="リリース希望日 (Cotrol+Shift+D)",
                    )
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.ACCOUNT_BOX, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.ACCOUNT_BOX_OUTLINED, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "自身の申請",
                        tooltip="自身の申請 (Cotrol+Shift+M)",
                    )
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(ft.Icons.LIST, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.LIST_OUTLINED, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "全て",
                        tooltip="全て (Cotrol+Shift+A)",
                    )
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.CHECK_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(ft.Icons.CHECK, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "完了",
                        tooltip="完了 (Cotrol+Shift+E)",
                    )
                ),
            ]

        if self.session.get('user_role') == UserRole.USER_ROLE:
            self.option_nav_rail_items = [
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.HISTORY_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.HISTORY, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "操作履歴",
                        tooltip="操作履歴 (Cotrol+Shift+H)",
                    )
                ),
            ]
        else:
            self.option_nav_rail_items = [
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.HISTORY_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.HISTORY, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "操作履歴",
                        tooltip="操作履歴 (Cotrol+Shift+H)",
                    )
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icon(
                        ft.Icons.SETTINGS_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.Icons.SETTINGS, size=self.ICON_SIZE),
                    label_content=ft.Text(
                        "設定",
                        tooltip="設定 (Cotrol+Shift+C)",
                    )
                ),
            ]
        self.main_nav_rail = ft.NavigationRail(
            height=self.MAIN_RAIL_HEIGHT,
            selected_index=default_selected_index,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=self.RAIL_MIN_WIDTH,
            min_extended_width=self.RAIL_MAX_WIDTH,
            # leading=ft.FloatingActionButton(icon=ft.Icons.CREATE, text="ダッシュボード"),
            bgcolor=ft.Colors.TRANSPARENT,
            group_alignment=-0.9,
            destinations=self.main_nav_rail_items,
            on_change=self.on_click_main_navigation_item,
        )
        self.option_nav_rail = ft.NavigationRail(
            height=self.OPTION_RAIL_HEIGHT,
            selected_index=None,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=self.RAIL_MIN_WIDTH,
            min_extended_width=self.RAIL_MAX_WIDTH,
            # leading=ft.FloatingActionButton(icon=ft.Icons.CREATE, text="ダッシュボード"),
            bgcolor=ft.Colors.TRANSPARENT,
            indicator_color=ft.Colors.TRANSPARENT,
            group_alignment=0,
            destinations=self.option_nav_rail_items,
            on_change=self.on_click_option_navigation_item,
        )
        self.toggle_nav_rail_button = ft.IconButton(
            icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_LEFT,
            icon_color=ft.Colors.BLUE_GREY_400,
            selected=False,
            selected_icon=ft.Icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
            on_click=self.toggle_nav_rail,
            tooltip="サイドバーを非表示",
        )

        # controls
        controls = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("申請メニュー"),
                ]),
                # divider
                ft.Container(
                    bgcolor=ft.Colors.BLACK26,
                    border_radius=ft.border_radius.all(30),
                    height=1,
                    alignment=ft.alignment.center_right,
                    # width=self.RAIL_MAX_WIDTH + 30
                ),
                self.main_nav_rail,
                # divider
                ft.Container(
                    bgcolor=ft.Colors.BLACK26,
                    border_radius=ft.border_radius.all(30),
                    height=1,
                    alignment=ft.alignment.center_right,
                    # width=self.RAIL_MAX_WIDTH + 30
                ),
                self.option_nav_rail,
            ], tight=True),
            padding=ft.padding.all(15),
            margin=ft.margin.all(0),
            # width=self.CONTENT_WIDTH,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border_radius=ft.border_radius.all(5),
        )
        self.register_key_shortcuts()
        super().__init__(controls)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        if self.session.get('user_role') == UserRole.USER_ROLE:
            # 最新の申請
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="L", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=0),
            )
            # リリース希望日順
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="D", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=1),
            )
            # 自身の申請
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="M", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=2),
            )
            # 全ての申請
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="A", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=3),
            )
            # 完了済みの申請
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="H", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_option_navigation_item, item_index=0),
            )
        else:
            # 最新の申請
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="L", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=0),
            )
            # リリース希望日順
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="D", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=1),
            )
            # 自身の申請
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="M", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=2),
            )
            # 全ての申請
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="A", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=3),
            )
            # 完了済みの申請
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="E", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_main_navigation_item, item_index=4),
            )
            # 操作履歴
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="H", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=partial(self.on_click_option_navigation_item, item_index=0),
            )

    def on_click_main_navigation_item(self, e, item_index=None):
        # キーボードショートカットから呼ばれた場合、
        # item_indexにセットされている値をNavigationRailDestinationのインデックスの代わりに利用する
        selected_index = item_index if item_index is not None else e.control.selected_index
        if self.session.get('user_role') == UserRole.USER_ROLE:
            match selected_index:
                case 0:
                    e.page.go('/latest_requests')
                case 1:
                    e.page.go('/deadline_requests')
                case 2:
                    e.page.go('/all_requests')
                case 3:
                    e.page.go('/completed_requests')
        else:
            match selected_index:
                case 0:
                    e.page.go('/latest_requests')
                case 1:
                    e.page.go('/deadline_requests')
                case 2:
                    e.page.go('/my_requests')
                case 3:
                    e.page.go('/all_requests')
                case 4:
                    e.page.go('/completed_requests')

    def on_click_option_navigation_item(self, e, item_index=None):
        # キーボードショートカットから呼ばれた場合、
        # item_indexにセットされている値をNavigationRailDestinationのインデックスの代わりに利用する
        selected_index = item_index if item_index is not None else e.control.selected_index
        if self.session.get('user_role') == UserRole.USER_ROLE:
            match selected_index:
                case 0:
                    e.page.go('/my_activities')
        elif self.session.get('user_role') != UserRole.USER_ROLE:
            match selected_index:
                case 0:
                    e.page.go('/all_activities')
                # case 1:
                #     e.page.go('/configurations')

    def toggle_nav_rail(self, e):
        self.main_nav_rail.visible = not self.main_nav_rail.visible
        self.toggle_nav_rail_button.selected = not self.toggle_nav_rail_button.selected
        self.toggle_nav_rail_button.tooltip = "サイドバーを表示" if self.toggle_nav_rail_button.selected else "サイドバーを非表示"
        self.page.update()
