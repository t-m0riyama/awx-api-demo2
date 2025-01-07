import os
import re

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.app_title import AppTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.types.user_role import UserRole
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.event_manager import EventManager
from awx_demo.utils.logging import Logging


class LoginForm(ft.Card):
    """Login フォーム"""

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    AWX_URL_DEFAULT = "https://awx.example.com"
    ADMIN_TEAM_DEFAULT = "requestmanager-admins"
    OPERATOR_TEAM_DEFAULT = "requestmanager-operators"
    USER_TEAM_DEFAULT = "requestmanager-users"
    APP_TITLE_DEFAULT = "AWX API Demo"

    def __init__(self, session, page: ft.Page, default_awx_url=AWX_URL_DEFAULT):
        self.session = session
        self.page = page
        self.default_awx_url = default_awx_url

        # controls
        default_awx_url = re.sub('/$', '', os.getenv("RMX_AWX_URL", self.AWX_URL_DEFAULT))
        app_title = os.getenv("RMX_APP_TITLE", self.APP_TITLE_DEFAULT).strip('"')
        self.tfLoginid = ParameterInputText(
            label="Login ID",
            value=(
                self.session.get("awx_loginid")
                if self.session.contains_key("awx_loginid")
                else ""
            ),
            on_submit=self.on_click_login,
        )
        self.tfPassword = ParameterInputText(
            label="Password",
            value=(
                self.session.get("awx_password")
                if self.session.contains_key("awx_password")
                else ""
            ),
            is_password=True,
            on_submit=self.on_click_login,
        )
        self.tfAWXUrl = ParameterInputText(
            label="AWX URL",
            value=(
                self.session.get("awx_url")
                if self.session.contains_key("awx_url")
                else default_awx_url
            ),
            on_submit=self.on_click_login,
        )
        self.txtLoginMessage = ft.Text(
            "ログイン失敗: 認証に失敗しました。ログインIDとパスワードを確認して下さい。",
            size=16,
            color=ft.Colors.ERROR,
            visible=False,
        )
        self.btnLogin = ft.FilledButton("ログイン", on_click=self.on_click_login)

        header = AppTitle(title=app_title, width=self.CONTENT_WIDTH)
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

        controls = ft.Container(
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
        )
        super().__init__(controls)

    @Logging.func_logger
    def on_click_login(self, e):
        loginid = self.tfLoginid.value
        password = self.tfPassword.value
        awx_url = self.tfAWXUrl.value
        if self.login_auth(awx_url, loginid, password):
            self.txtLoginMessage.visible = False
            self.txtLoginMessage.update()
            self.session.set("awx_loginid", loginid)
            self.session.set("awx_password", password)
            self.session.set("awx_url", awx_url)
            e.page.go("/latest_requests")

    @Logging.func_logger
    def show_login_failed_message(self, reason):
        message = ''
        match reason:
            case AWXApiHelper.API_FAILED_STATUS:
                message = "ログイン失敗: 認証に失敗しました。ログインIDとパスワードを確認して下さい。"
                title_suffix = "認証エラー"
            case AWXApiHelper.API_FAILED_TO_CONNECT:
                message = "ログイン失敗: AWXサーバーに接続できません。AWX URLを確認して下さい。"
                title_suffix = "接続エラー"
            case _:
                message = "ログイン失敗: AWXサーバーに接続できません。管理者に連絡し、ログを確認してください。"
                title_suffix = "接続エラー"

        self.txtLoginMessage.value = message
        self.txtLoginMessage.visible = True
        app_title = os.getenv("RMX_APP_TITLE", self.APP_TITLE_DEFAULT).strip('"')
        self.page.title = f"{app_title} - {title_suffix}"
        self.page.update()

    @Logging.func_logger
    def show_lack_authority_message(self):
        self.txtLoginMessage.value = "ログイン失敗: 指定したユーザには、ログインする権限がありません。ログインIDとパスワードを確認して下さい。"
        self.txtLoginMessage.visible = True
        self.txtLoginMessage.update()

    @Logging.func_logger
    def login_auth(self, awx_url, loginid, password):
        login_result, reason = AWXApiHelper.login(awx_url, loginid, password)
        if not login_result:
            summary = ''
            match reason:
                case AWXApiHelper.API_FAILED_STATUS:
                    summary = "ログインに失敗しました。認証に失敗しました。ログインIDとパスワードを確認して下さい。"
                case AWXApiHelper.API_FAILED_TO_CONNECT:
                    summary = "ログインに失敗しました。AWXサーバーに接続できません。AWX URLを確認して下さい。"
                case _:
                    summary = "ログインに失敗しました。AWXサーバーに接続できません。管理者に連絡し、ログを確認してください。"

            activity_spec = ActivityHelper.ActivitySpec(
                user=loginid,
                request_id="",
                activity_type=EventType.LOGIN,
                status=EventStatus.FAILED,
                summary=summary,
                detail="",
            )
            EventManager.emit_event(
                activity_spec=activity_spec,
                notification_specs=[],
            )
            self.show_login_failed_message(reason)
            return False
        teams = AWXApiHelper.get_teams_user_belong(awx_url, loginid, password)
        role = self.check_role(teams)

        if role is None:
            summary = "ログインに失敗しました。指定したユーザには、ログインする権限がありません。ログインIDとパスワードを確認して下さい。"
            activity_spec = ActivityHelper.ActivitySpec(
                user=loginid,
                request_id="",
                activity_type=EventType.LOGIN,
                status=EventStatus.FAILED,
                summary=summary,
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
                activity_type=EventType.LOGIN,
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

    @Logging.func_logger
    def check_role(self, teams):
        is_admin = False
        is_operator = False
        is_user = False

        # AWX/AAPのチーム名を環境変数で指定している場合、変更する
        admin_team_name = os.getenv("RMX_ADMIN_TEAM_NAME", self.ADMIN_TEAM_DEFAULT)
        operator_team_name = os.getenv("RMX_OPERATOR_TEAM_NAME", self.OPERATOR_TEAM_DEFAULT)
        user_team_name = os.getenv("RMX_USER_TEAM_NAME", self.USER_TEAM_DEFAULT)

        for team in teams:
            if team == admin_team_name:
                is_admin = True
            elif team == operator_team_name:
                is_operator = True
            elif team == user_team_name:
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
