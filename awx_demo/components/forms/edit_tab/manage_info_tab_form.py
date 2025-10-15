import os

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class ManageInfoTabForm(ft.Card):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    FILTERED_IAAS_USERS_DEFAULT = "root,admin,awxcli"

    def __init__(
        self,
        session,
        height=CONTENT_HEIGHT,
        width=CONTENT_WIDTH,
        body_height=BODY_HEIGHT,
    ):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height

        # controls
        filtered_users = os.getenv("RMX_FILTERED_IAAS_USERS", self.FILTERED_IAAS_USERS_DEFAULT).strip('"').strip("'").split(",")
        filtered_users = list(map(lambda s: s.strip(), filtered_users))
        iaas_users = AWXApiHelper.get_users(
            self.session.get("awx_url"),
            self.session.get("awx_loginid"),
            self.session.get("awx_password"),
            filtered_users,
        )
        # iaas_users = []  # for DEBUG
        iaas_user_options = []
        for iaas_user in iaas_users:
            iaas_user_options.append(ft.dropdown.Option(iaas_user["username"]))

        iaas_user_change_disabled = False if self.session.get("user_role") == UserRole.ADMIN_ROLE else True
        self.dropIaasUser = ft.Dropdown(
            label="作業担当者",
            value=(self.session.get("iaas_user") if self.session.contains_key("iaas_user") else ""),
            options=iaas_user_options,
            hint_text="Iaas作業担当者のアカウントを指定します。",
            on_change=self.on_change_iaas_user,
            disabled=iaas_user_change_disabled,
            autofocus=True,
        )

        status_change_disabled = False if self.session.get("user_role") == UserRole.ADMIN_ROLE else True
        self.dropRequestStatus = ft.Dropdown(
            label="申請の状態",
            value=(RequestStatus.to_friendly(self.session.get("request_status")) if self.session.contains_key("request_status") else ""),
            options=[
                ft.dropdown.Option(RequestStatus.START_FRIENDLY),
                ft.dropdown.Option(RequestStatus.APPROVED_FRIENDLY),
                ft.dropdown.Option(RequestStatus.APPLYING_FAILED_FRIENDLY),
                ft.dropdown.Option(RequestStatus.COMPLETED_FRIENDLY),
            ],
            hint_text="申請の状態を指定します。",
            on_change=self.on_change_request_status,
            disabled=status_change_disabled,
            autofocus=True,
        )
        self.textJobId = ft.Text(
            value=("最新のジョブID: " + str(self.session.get("job_id")) if self.session.contains_key("job_id") else "ジョブID: (未実行)"),
        )
        self.btnAWXJobLink = ft.TextButton(
            text="ジョブ出力の参照: " + self.session.get("awx_url") + "/#/jobs/playbook/{}/output".format(self.session.get("job_id")),
            url=self.session.get("awx_url") + "/#/jobs/playbook/{}/output".format(self.session.get("job_id")),
            visible=True if self.session.contains_key("job_id") else False,
        )

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get("user_role") == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                self.dropIaasUser,
                self.dropRequestStatus,
                self.textJobId,
                self.btnAWXJobLink,
            ],
            height=self.body_height,
            disabled=change_disabled,
        )

        controls = ft.Container(
            ft.Column(
                [
                    body,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=self.content_width,
            height=self.content_height,
            padding=30,
        )
        super().__init__(controls)

    @Logging.func_logger
    def on_change_iaas_user(self, e):
        self.session.set("iaas_user", e.control.value)

    @Logging.func_logger
    def on_change_request_status(self, e):
        self.session.set("request_status", RequestStatus.to_formal(e.control.value))
