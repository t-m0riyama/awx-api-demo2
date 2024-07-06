import datetime

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.utils.logging import Logging


class CreateRequestForm(ft.UserControl):

    # const
    CONTENT_HEIGHT = 550
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 300
    START_DATE_DAYS = 7
    END_DATE_DAYS = 30

    def __init__(self, session, page: ft.Page, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel

        # initialize Job options
        if not self.session.contains_key('job_options'):
            self.session.set('job_options', {})

        # overlay settings
        start_date = datetime.datetime.now() + datetime.timedelta(days=self.START_DATE_DAYS)
        end_date = datetime.datetime.now() + datetime.timedelta(days=self.END_DATE_DAYS)
        current_date = self.session.get('request_deadline') if self.session.contains_key(
            'request_deadline') else start_date
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
        super().__init__()

    def build(self):
        formTitle = FormTitle('申請の追加', '申請項目の種類を選択', self.content_width)
        formDescription = FormDescription('新しく申請を作成します。')
        self.tfRequestText = ParameterInputText(
            value=self.session.get('request_text') if self.session.contains_key(
                'request_text') else '',
            label='依頼内容',
            hint_text='ご依頼内容を簡潔に記載してください。 例)ABCシステムのWEBサーバ構築')
        self.dropCategory = ft.Dropdown(
            label='依頼区分',
            value=self.session.get('request_category') if self.session.contains_key(
                'request_category') else 'サーバに対する変更',
            options=[
                ft.dropdown.Option('新規サーバの構築', disabled=True),
                ft.dropdown.Option('サーバに対する変更'),
                ft.dropdown.Option('バックアップの停止', disabled=True),
                ft.dropdown.Option('特権IDの払い出し', disabled=True),
            ],
        )
        self.dropOperation = ft.Dropdown(
            label='申請項目',
            value=self.session.get('request_operation') if self.session.contains_key(
                'request_operation') else 'CPUコア/メモリ割り当て変更',
            options=[
                ft.dropdown.Option('CPUコア/メモリ割り当て変更'),
            ],
        )
        self.lblReleseDeadline = ft.Text(
            value=('リリース希望日: ' + self.session.get('request_deadline').strftime('%Y/%m/%d')
                   ) if self.session.contains_key('request_deadline') else 'リリース希望日:(未指定)',
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            color=ft.colors.PRIMARY,
        )
        self.btnRequestDeadline = ft.FilledTonalButton(
            '希望日の指定',
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: self.dpRequestDeadline.pick_date(),
        )
        self.btnNext = ft.FilledButton(
            '次へ',
            on_click=self.on_click_next,
            disabled=False if self.dpRequestDeadline.value else True,
        )
        self.btnCancel = ft.ElevatedButton(
            'キャンセル', on_click=self.on_click_cancel)

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
                self.tfRequestText,
                self.dropCategory,
                self.dropOperation,
                ft.Row(
                    [
                        self.lblReleseDeadline,
                        self.btnRequestDeadline,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                ),
            ],
            height=self.body_height,
        )
        footer = ft.Row(
            [
                self.btnCancel,
                self.btnNext,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        return ft.Card(
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
                width=self.content_width,
                height=self.content_height,
                padding=30,
            ),
        )

    @Logging.func_logger
    def on_change_request_deadline(self, e):
        self.lblReleseDeadline.value = 'リリース希望日: ' + \
            self.dpRequestDeadline.value.strftime('%Y/%m/%d')
        if self.dpRequestDeadline.value:
            self.btnNext.disabled = False
        else:
            self.btnNext.disabled = True
        self.lblReleseDeadline.update()
        self.btnNext.update()

    @Logging.func_logger
    def on_click_cancel(self, e):
        self.step_change_cancel(e)

    @Logging.func_logger
    def on_click_next(self, e):
        self.session.set('request_text', self.tfRequestText.value)
        self.session.set('request_category', self.dropCategory.value)
        self.session.set('request_operation', self.dropOperation.value)
        if self.dpRequestDeadline.value:
            self.session.set('request_deadline', self.dpRequestDeadline.value)
        self.step_change_next(e)
