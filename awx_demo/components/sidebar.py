import flet as ft

from awx_demo.components.types.user_role import UserRole


class Sidebar(ft.UserControl):

    # const
    CONTENT_HEIGHT = 640
    CONTENT_WIDTH = 140
    RAIL_MAX_WIDTH = 130
    RAIL_MIN_WIDTH = 0
    MAIN_RAIL_HEIGHT = 380
    OPTION_RAIL_HEIGHT = 120
    ICON_SIZE = 28

    def __init__(self, session, default_selected_index=0):
        self.session = session
        super().__init__()
        self.nav_rail_visible = True
        if self.session.get('user_role') == UserRole.USER_ROLE:
            self.main_nav_rail_items = [
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.FIBER_NEW, size=self.ICON_SIZE),
                    selected_icon_content=ft.Icon(
                        ft.icons.FIBER_NEW_OUTLINED, size=self.ICON_SIZE),
                    label="最新"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.WARNING_AMBER, size=self.ICON_SIZE),
                    selected_icon_content=ft.Icon(
                        ft.icons.WARNING_AMBER_OUTLINED, size=self.ICON_SIZE),
                    label="リリース希望日"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.LIST, size=self.ICON_SIZE),
                    selected_icon_content=ft.Icon(
                        ft.icons.LIST_OUTLINED, size=self.ICON_SIZE),
                    label="全て"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.CHECK_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(ft.icons.CHECK, size=self.ICON_SIZE),
                    label="完了"
                ),
            ]
        else:
            self.main_nav_rail_items = [
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.FIBER_NEW, size=self.ICON_SIZE),
                    selected_icon_content=ft.Icon(
                        ft.icons.FIBER_NEW_OUTLINED, size=self.ICON_SIZE),
                    label="最新"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.WARNING_AMBER, size=self.ICON_SIZE),
                    selected_icon_content=ft.Icon(
                        ft.icons.WARNING_AMBER_OUTLINED, size=self.ICON_SIZE),
                    label="リリース希望日"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.ACCOUNT_BOX, size=self.ICON_SIZE),
                    selected_icon_content=ft.Icon(
                        ft.icons.ACCOUNT_BOX_OUTLINED, size=self.ICON_SIZE),
                    label="自身の申請"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(ft.icons.LIST, size=self.ICON_SIZE),
                    selected_icon_content=ft.Icon(
                        ft.icons.LIST_OUTLINED, size=self.ICON_SIZE),
                    label="全て"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.CHECK_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(ft.icons.CHECK, size=self.ICON_SIZE),
                    label="完了"
                ),
            ]

        if self.session.get('user_role') == UserRole.USER_ROLE:
            self.option_nav_rail_items = [
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.HISTORY_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.icons.HISTORY, size=self.ICON_SIZE),
                    label="操作履歴"
                ),
            ]
        else:
            self.option_nav_rail_items = [
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.HISTORY_OUTLINED, size=self.ICON_SIZE),
                    selected_icon=ft.Icon(
                        ft.icons.HISTORY, size=self.ICON_SIZE),
                    label="操作履歴"
                ),
                ft.NavigationRailDestination(
                    icon_content=ft.Icon(
                        ft.icons.SETTINGS_OUTLINED, size=self.ICON_SIZE),
                    selected_icon_content=ft.Icon(
                        ft.icons.SETTINGS, size=self.ICON_SIZE),
                    label_content=ft.Text("設定"),
                ),
            ]
        self.main_nav_rail = ft.NavigationRail(
            height=self.MAIN_RAIL_HEIGHT,
            selected_index=default_selected_index,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=self.RAIL_MIN_WIDTH,
            min_extended_width=self.RAIL_MAX_WIDTH,
            # leading=ft.FloatingActionButton(icon=ft.icons.CREATE, text="ダッシュボード"),
            bgcolor=ft.colors.TRANSPARENT,
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
            # leading=ft.FloatingActionButton(icon=ft.icons.CREATE, text="ダッシュボード"),
            bgcolor=ft.colors.TRANSPARENT,
            indicator_color=ft.colors.TRANSPARENT,
            group_alignment=0,
            destinations=self.option_nav_rail_items,
            on_change=self.on_click_option_navigation_item,
        )
        self.toggle_nav_rail_button = ft.IconButton(
            icon=ft.icons.KEYBOARD_DOUBLE_ARROW_LEFT,
            icon_color=ft.colors.BLUE_GREY_400,
            selected=False,
            selected_icon=ft.icons.KEYBOARD_DOUBLE_ARROW_RIGHT,
            on_click=self.toggle_nav_rail,
            tooltip="サイドバーを非表示",
        )

    def on_click_main_navigation_item(self, e):
        if self.session.get('user_role') == UserRole.USER_ROLE:
            match e.control.selected_index:
                case 0:
                    e.page.go('/latest_requests')
                case 1:
                    e.page.go('/deadline_requests')
                case 2:
                    e.page.go('/all_requests')
                case 3:
                    e.page.go('/completed_requests')
        else:
            match e.control.selected_index:
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

    def on_click_option_navigation_item(self, e):
        if self.session.get('user_role') == UserRole.USER_ROLE:
            match e.control.selected_index:
                case 0:
                    e.page.go('/my_activities')
        elif self.session.get('user_role') != UserRole.USER_ROLE:
            match e.control.selected_index:
                case 0:
                    e.page.go('/all_activities')
                case 1:
                    e.page.go('/configurations')

    def build(self):
        self.view = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("申請メニュー"),
                ]),
                # divider
                ft.Container(
                    bgcolor=ft.colors.BLACK26,
                    border_radius=ft.border_radius.all(30),
                    height=1,
                    alignment=ft.alignment.center_right,
                    # width=self.RAIL_MAX_WIDTH + 30
                ),
                self.main_nav_rail,
                # divider
                ft.Container(
                    bgcolor=ft.colors.BLACK26,
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
            bgcolor=ft.colors.SURFACE_VARIANT,
            border_radius=ft.border_radius.all(5),
        )
        return self.view

    def toggle_nav_rail(self, e):
        self.main_nav_rail.visible = not self.main_nav_rail.visible
        self.toggle_nav_rail_button.selected = not self.toggle_nav_rail_button.selected
        self.toggle_nav_rail_button.tooltip = "サイドバーを表示" if self.toggle_nav_rail_button.selected else "Collapse Side Bar"
        self.view.update()
        self.page.update()
