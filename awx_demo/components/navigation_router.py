import flet as ft

from awx_demo.components.app_header import AppHeader
from awx_demo.components.forms.all_activity_list_form import AllActivityListForm
from awx_demo.components.forms.all_request_list_form import AllRequestListForm
from awx_demo.components.forms.completed_request_list_form import CompletedRequestListForm
from awx_demo.components.forms.deadline_request_list_form import DeadlineRequestListForm
from awx_demo.components.forms.latest_request_list_form import LatestRequestListForm
from awx_demo.components.forms.my_activity_list_form import MyActivityListForm
from awx_demo.components.forms.my_request_list_form import MyRequestListForm
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.sidebar import Sidebar
from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.logging import Logging


class NavigationRouter:
    """アニメーションの発生しないView遷移を実現する
    Viewの遷移の際、page.views.appendを利用する場合はアニメーションを無効化できないことを回避するため、
    コントロールの再作成を行う。
    """

    def __init__(self, session, page: ft.Page, app_title_base, dlgLogin):
        self.session = session
        self.page = page
        self.app_title_base = app_title_base
        self.dlgLogin = dlgLogin

    def route_change(self):
        template_route = ft.TemplateRoute(self.page.route)
        self.page.controls.clear()
        formRequests = None

        if template_route.match('/login'):
            self.page.open(self.dlgLogin)
            self.dlgLogin.open = True
            self.page.update()
        else:
            if SessionHelper.logout_if_session_expired(self.page, self.session): return
            self.dlgLogin.open = False
            if self.session.get('user_role') == UserRole.USER_ROLE:
                match template_route.route:
                    case '/latest_requests':
                        formRequests = LatestRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - 最新の申請"
                        navigation_selected_index = 0
                    case '/deadline_requests':
                        formRequests = DeadlineRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - リリース希望日順"
                        navigation_selected_index = 1
                    case '/all_requests':
                        formRequests = AllRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - すべての申請"
                        navigation_selected_index = 2
                    case '/completed_requests':
                        formRequests = CompletedRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - 完了済みの申請"
                        navigation_selected_index = 3
                    case '/my_activities':
                        formRequests = MyActivityListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - 操作履歴"
                        navigation_selected_index = 0
                    case _:
                        Logging.error("error undefined route")
                        navigation_selected_index = 0
            else:
                match template_route.route:
                    case '/latest_requests':
                        formRequests = LatestRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - 最新の申請"
                        navigation_selected_index = 0
                    case '/deadline_requests':
                        formRequests = DeadlineRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - リリース希望日順"
                        navigation_selected_index = 1
                    case '/my_requests':
                        formRequests = MyRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - 自身の申請"
                        navigation_selected_index = 2
                    case '/all_requests':
                        formRequests = AllRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - すべての申請"
                        navigation_selected_index = 3
                    case '/completed_requests':
                        formRequests = CompletedRequestListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - 完了済みの申請"
                        navigation_selected_index = 4
                    case '/all_activities':
                        formRequests = AllActivityListForm(
                            self.session, self.page)
                        self.page.title = f"{self.app_title_base} - 操作履歴"
                        navigation_selected_index = 0
                    case _:
                        Logging.error("error undefined route")
                        navigation_selected_index = 0

            layout = ft.ResponsiveRow(
                controls=[
                    ft.Column(col={
                                  "sm": 2, "md": 2, "lg": 2, "xl": 2, "xxl": 1
                              },
                              controls=[Sidebar(self.session, navigation_selected_index)]),
                    ft.Column(col={
                                  "sm": 10, "md": 10, "lg": 10, "xl": 10, "xxl": 11
                              },
                              controls=[formRequests]),
                ],
                spacing=30,
                vertical_alignment=ft.CrossAxisAlignment.START,  # 画面上部から表示
            )

            AppHeader(self.session, self.page, self.app_title_base)
            self.session.set('request_text_search_string', '')
            self.page.add(layout)
            self.page.update()
