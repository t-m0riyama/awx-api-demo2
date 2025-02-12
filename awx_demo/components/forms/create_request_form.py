import datetime
import os

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.db_helper.types.request_category import RequestCategory, RequestOperation
from awx_demo.utils.logging import Logging


class CreateRequestForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 550
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 300
    START_DATE_DAYS_DEFAULT = 7
    END_DATE_DAYS_DEFAULT = 30

    def __init__(self, session, page: ft.Page, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT,
                 step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel
        self.wizard_card_start = True

        # initialize Job options
        if not self.session.contains_key('job_options'):
            self.session.set('job_options', {})

        # overlay settings
        start_date_days = int(os.getenv("RMX_DEADLINE_START_DATE_DAYS", self.START_DATE_DAYS_DEFAULT))
        end_date_days = int(os.getenv("RMX_DEADLINE_END_DATE_DAYS", self.END_DATE_DAYS_DEFAULT))
        start_date = datetime.datetime.now() + datetime.timedelta(days=start_date_days)
        end_date = datetime.datetime.now() + datetime.timedelta(days=end_date_days)
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
            value=current_date,
        )
        self.page.overlay.append(self.dpRequestDeadline)

        # Controls
        formTitle = FormTitle('申請の追加', '申請項目の種類を選択')
        formDescription = FormDescription('新しく申請を作成します。＊は入力/選択が必須の項目です。')
        self.tfRequestText = ParameterInputText(
            value=self.session.get('request_text') if self.session.contains_key(
                'request_text') else '',
            label='依頼内容',
            max_length=80,
            hint_text='ご依頼内容を簡潔に記載してください。 例)ABCシステムのWEBサーバCPU増設',
            on_submit=self.on_click_next,
        )
        self.dropCategory = ft.Dropdown(
            label='依頼区分(＊)',
            value=self.session.get('request_category') if self.session.contains_key(
                'request_category') else 'サーバに対する変更',
            # autofocus=True,
            options=[
                ft.dropdown.Option(RequestCategory.VM_CREATE_FRIENDLY, disabled=True),
                ft.dropdown.Option(RequestCategory.VM_SETTING_CHANGE_FRIENDLY),
                ft.dropdown.Option(RequestCategory.BACKUP_STOP_OR_RESUME_FRIENDLY, disabled=True),
                ft.dropdown.Option(RequestCategory.PRIVILEGED_ID_CREATE_FRIENDLY, disabled=True),
            ],
        )
        self.dropOperation = ft.Dropdown(
            label='申請項目(＊)',
            value=self.session.get('request_operation') if self.session.contains_key(
                'request_operation') else RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY,
            # autofocus=True,
            options=[
                ft.dropdown.Option(RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY),
                ft.dropdown.Option(RequestOperation.VM_START_OR_STOP_FRIENDLY),
            ],
        )
        self.lblRequestDeadline = ft.Text(
            value=(f"リリース希望日(＊): {self.session.get('request_deadline').strftime('%Y/%m/%d')}"
                   ) if self.session.contains_key('request_deadline') else f"リリース希望日(＊): {start_date.strftime('%Y/%m/%d')}",
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            color=ft.Colors.PRIMARY,
        )
        self.btnRequestDeadline = ft.FilledTonalButton(
            '希望日の指定',
            icon=ft.Icons.CALENDAR_MONTH,
            # autofocus=True,
            on_click=lambda _: self.page.open(
                self.dpRequestDeadline
            ),
        )
        self.btnNext = ft.FilledButton(
            '次へ', tooltip='次へ (Shift+Alt+N)', on_click=self.on_click_next)
        self.btnCancel = ft.ElevatedButton(
            'キャンセル', tooltip='キャンセル (Shift+Alt+X)', on_click=self.on_click_cancel)

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
                        self.lblRequestDeadline,
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

        controls = ft.Container(
            ft.SelectionArea(
                content=ft.Column(
                    [
                        header,
                        body,
                        ft.Divider(),
                        footer,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ),
            width=self.content_width,
            height=self.content_height,
            padding=30,
        )
        super().__init__(controls)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=lambda e: self.tfRequestText.focus(),
        )
        super().register_key_shortcuts()

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=False, alt=True, meta=False
            ),
        )
        super().unregister_key_shortcuts()

    @Logging.func_logger
    def on_change_request_deadline(self, e):
        self.lblRequestDeadline.value = 'リリース希望日: ' + \
            self.dpRequestDeadline.value.strftime('%Y/%m/%d')
        self.lblRequestDeadline.update()

    @Logging.func_logger
    def on_click_next(self, e):
        self.session.set('request_text', self.tfRequestText.value)
        self.session.set('request_category', self.dropCategory.value)
        self.session.set('request_operation', self.dropOperation.value)
        self.session.set('request_deadline', self.dpRequestDeadline.value)
        self.step_change_next(e)
