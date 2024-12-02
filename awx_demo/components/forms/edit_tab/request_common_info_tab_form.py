import datetime
import os

import flet as ft

from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.types.user_role import UserRole
from awx_demo.db_helper.types.request_category import RequestCategory, RequestOperation
from awx_demo.utils.logging import Logging


class RequestCommonInfoTabForm(ft.Card):

    # const
    CONTENT_HEIGHT = 550
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 300
    START_DATE_DAYS_DEFAULT = 7
    END_DATE_DAYS_DEFAULT = 30

    def __init__(self, session, page: ft.Page, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height

        # initialize Job options
        if not self.session.contains_key('job_options'):
            self.session.set('job_options', {})

        # overlay settings
        start_date_days = int(os.getenv("RMX_DEADLINE_START_DATE_DAYS", self.START_DATE_DAYS_DEFAULT))
        end_date_days = int(os.getenv("RMX_DEADLINE_END_DATE_DAYS", self.END_DATE_DAYS_DEFAULT))
        start_date = datetime.datetime.now() + datetime.timedelta(days=start_date_days)
        end_date = datetime.datetime.now() + datetime.timedelta(days=end_date_days)
        current_date = self.session.get('request_deadline') if self.session.contains_key('request_deadline') else start_date
        self.dpRequestDeadline = ft.DatePicker(
            on_change=self.on_change_request_deadline,
            # on_dismiss=date_picker_dismissed,
            first_date=datetime.datetime(
                start_date.year, start_date.month, start_date.day),
            last_date=datetime.datetime(
                end_date.year, end_date.month, end_date.day),
            current_date=current_date,
        )
        self.page.overlay.append(self.dpRequestDeadline)

        # controls
        self.textRequestId = ft.Text(
            value=('申請ID: ' + self.session.get('request_id')),
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            color=ft.colors.PRIMARY,
        )
        self.textRequestDate = ft.Text(
            value=('申請日: ' + self.session.get('request_date').strftime('%Y/%m/%d %H:%M')
                   ) if self.session.contains_key('request_date') else '申請日:(未指定)',
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            color=ft.colors.PRIMARY,
        )
        self.textUpdated = ft.Text(
            value=('最終更新日: ' + self.session.get('updated').strftime('%Y/%m/%d %H:%M')
                   ) if self.session.contains_key('updated') else '最終更新日:(未指定)',
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            color=ft.colors.PRIMARY,
        )
        self.tfRequestText = ParameterInputText(
            value=self.session.get('request_text') if self.session.contains_key(
                'request_text') else '',
            label='依頼内容',
            max_length=80,
            hint_text='ご依頼内容を簡潔に記載してください。 例)ABCシステムのWEBサーバ構築',
            on_change=self.on_change_request_text)
        self.dropCategory = ft.Dropdown(
            label='依頼区分',
            value=self.session.get('request_category') if self.session.contains_key(
                'request_category') else RequestCategory.VM_SETTING_CHANGE_FRIENDLY,
            options=[
                ft.dropdown.Option(RequestCategory.VM_CREATE_FRIENDLY, disabled=True),
                ft.dropdown.Option(RequestCategory.VM_SETTING_CHANGE_FRIENDLY),
                ft.dropdown.Option(RequestCategory.BACKUP_STOP_OR_RESUME_FRIENDLY, disabled=True),
                ft.dropdown.Option(RequestCategory.PRIVILEGED_ID_CREATE_FRIENDLY, disabled=True),
            ],
            disabled=True,
        )
        self.dropOperation = ft.Dropdown(
            label='申請項目',
            value=self.session.get('request_operation') if self.session.contains_key(
                'request_operation') else RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY,
            options=[
                ft.dropdown.Option(RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY),
            ],
            disabled=True,
        )
        self.textRequestDeadline = ft.Text(
            value=('リリース希望日: ' + self.session.get('request_deadline').strftime('%Y/%m/%d')
                   ) if self.session.contains_key('request_deadline') else 'リリース希望日:(未指定)',
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            color=ft.colors.PRIMARY,
        )
        self.btnRequestDeadline = ft.FilledTonalButton(
            '希望日の指定',
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.page.open(
                self.dpRequestDeadline
            ),
        )

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get(
            'user_role') == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                ft.Row(
                    [
                        self.textRequestId,
                        self.textRequestDate,
                        self.textUpdated,
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                self.tfRequestText,
                self.dropCategory,
                self.dropOperation,
                ft.Row(
                    [
                        self.textRequestDeadline,
                        self.btnRequestDeadline,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
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
    def on_change_request_text(self, e):
        self.session.set('request_text', e.control.value)

    @Logging.func_logger
    def on_change_request_deadline(self, e):
        self.session.set('request_deadline', self.dpRequestDeadline.value)
        self.textRequestDeadline.value = 'リリース希望日: ' + \
            self.session.get('request_deadline').strftime('%Y/%m/%d')
        self.textRequestDeadline.update()
