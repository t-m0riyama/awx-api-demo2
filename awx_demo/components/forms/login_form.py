import os

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.app_title import AppTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.types.user_role import UserRole
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.event_manager import EventManager


class LoginForm(ft.UserControl):
    """Login フォーム"""

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    DEFAULT_AWX_URL = "https://awx.example.com"
    ADMIN_TEAM_NAME = "requestmanager-admins"
    OPERATOR_TEAM_NAME = "requestmanager-operators"
    USER_TEAM_NAME = "requestmanager-users"

    def __init__(self, session, page: ft.Page, default_awx_url=DEFAULT_AWX_URL):
        self.session = session
        self.page = page
        self.default_awx_url = default_awx_url
        super().__init__()

    def build(self):
        default_awx_url = os.getenv("AWX_URL", self.DEFAULT_AWX_URL)
        self.tfLoginid = ParameterInputText(
            label="Login ID",
            value=(
                self.session.get("awx_loginid")
                if self.session.contains_key("awx_loginid")
                else ""
            ),
            on_submit=self.login_clicked,
        )
        self.tfPassword = ParameterInputText(
            label="Password",
            value=(
                self.session.get("awx_password")
                if self.session.contains_key("awx_password")
                else ""
            ),
            is_password=True,
            on_submit=self.login_clicked,
        )
        self.tfAWXUrl = ParameterInputText(
            label="AWX URL",
            value=(
                self.session.get("awx_url")
                if self.session.contains_key("awx_url")
                else default_awx_url
            ),
            on_submit=self.login_clicked,
        )
        self.txtLoginMessage = ft.Text(
            "ログイン失敗: 認証に失敗しました。ログインIDとパスワードを確認して下さい。",
            size=16,
            color=ft.colors.ERROR,
            visible=False,
        )
        self.btnLogin = ft.FilledButton("ログイン", on_click=self.login_clicked)

        header = AppTitle(title="AWX API Demo", width=self.CONTENT_WIDTH)
        body = ft.Column(
            [
                self.tfLoginid,
                self.tfPassword,
                self.tfAWXUrl,
                self.txtLoginMessage,
            ],
            height=self.BODY_HEIGHT,
        )
        footer = ft.Row(
            [
                self.btnLogin,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.contents = ft.Card(
            ft.Container(
                ft.Column(
                    [
                        header,
                        body,
                        ft.Divider(),
                        footer,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                width=self.CONTENT_WIDTH,
                height=self.CONTENT_HEIGHT,
                padding=30,
            ),
        )
        return self.contents

    def login_clicked(self, e):
        loginid = self.tfLoginid.value
        password = self.tfPassword.value
        awx_url = self.tfAWXUrl.value
        if self.login_auth(awx_url, loginid, password):
            self.txtLoginMessage.visible = False
            self.contents.update()
            self.session.set("awx_loginid", loginid)
            self.session.set("awx_password", password)
            self.session.set("awx_url", awx_url)
            e.page.go("/latest_requests")

    def close_dlg(self, e):
        self.dlgAuthFailed.open = False
        self.page.update()

    def show_login_failed_message(self):
        self.txtLoginMessage.value = (
            "ログイン失敗: 認証に失敗しました。ログインIDとパスワードを確認して下さい。"
        )
        self.txtLoginMessage.visible = True
        self.contents.update()

    def show_lack_authority_message(self):
        self.txtLoginMessage.value = "ログイン失敗: 指定したユーザには、ログインする権限がありません。ログインIDとパスワードを確認して下さい。"
        self.txtLoginMessage.visible = True
        self.contents.update()

    def login_auth(self, awx_url, loginid, password):
        login_result = AWXApiHelper.login(awx_url, loginid, password)
        if not login_result:
            activity_spec = ActivityHelper.ActivitySpec(
                user=loginid,
                request_id="",
                event_type=EventType.LOGIN,
                status=EventStatus.FAILED,
                summary="ログインに失敗しました。認証に失敗しました。ログインIDとパスワードを確認して下さい。",
                detail="",
            )
            EventManager.emit_event(
                activity_spec=activity_spec,
                notification_specs=[],
            )
            self.show_login_failed_message()
            return False
        teams = AWXApiHelper.get_teams_user_belong(awx_url, loginid, password)
        role = self.check_role(teams)

        if role is None:
            activity_spec = ActivityHelper.ActivitySpec(
                user=loginid,
                request_id="",
                event_type=EventType.LOGIN,
                status=EventStatus.FAILED,
                summary="ログインに失敗しました。指定したユーザには、ログインする権限がありません。ログインIDとパスワードを確認して下さい。",
                detail="",
            )
            EventManager.emit_event(
                activity_spec=activity_spec,
                notification_specs=[],
            )
            self.show_lack_authority_message()
            return False
        else:
            self.session.set("user_role", role)
            activity_spec = ActivityHelper.ActivitySpec(
                user=loginid,
                request_id="",
                event_type=EventType.LOGIN,
                status=EventStatus.SUCCEED,
                summary="ログインに成功しました。{}ロールが付与されました。".format(
                    self.session.get("user_role")
                ),
                detail="",
            )
            EventManager.emit_event(
                activity_spec=activity_spec,
                notification_specs=[],
            )
            return login_result

    def check_role(self, teams):
        is_admin = False
        is_operator = False
        is_user = False

        for team in teams:
            if team == self.ADMIN_TEAM_NAME:
                is_admin = True
            elif team == self.OPERATOR_TEAM_NAME:
                is_operator = True
            elif team == self.USER_TEAM_NAME:
                is_user = True

        # より高い権限を持つロールに合致した場合、優先的に返す
        if is_admin:
            return UserRole.ADMIN_ROLE
        elif is_operator:
            return UserRole.OPERATOR_ROLE
        elif is_user:
            return UserRole.USER_ROLE
        else:
            return None
