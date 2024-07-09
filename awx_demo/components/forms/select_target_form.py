import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.logging import Logging


class SelectTargetForm(ft.UserControl):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VMS_LENGTH_MAX = 120

    def __init__(self, session, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel
        super().__init__()

    def build(self):
        formTitle = FormTitle('変更対象の選択', 'クラスタと仮想マシンの指定', self.content_width)
        formDescription = FormDescription('変更対象の仮想マシンと稼働するクラスタを指定します。クラスタは作業時に担当者が指定します。')

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = (
            True if self.session.get("user_role") == UserRole.USER_ROLE else False
        )
        self.dropCluster = ft.Dropdown(
            label='クラスタ',
            value=self.session.get('job_options')['vsphere_cluster'] if 'vsphere_cluster' in self.session.get('job_options') else '指定なし',
            options=[
                ft.dropdown.Option("指定なし"),
                ft.dropdown.Option("cluster-1"),
                ft.dropdown.Option("cluster-99"),
            ],
            hint_text='仮想マシンの稼働するクラスタ名を指定します。',
            disabled=change_disabled,
        )
        self.tfVms = ParameterInputText(
            value=self.session.get('job_options')[
                'target_vms'] if 'target_vms' in self.session.get('job_options') else '',
            label='仮想マシン',
            hint_text='仮想マシンを指定します。複数の仮想マシンは、「,」で区切ることで指定できます。',
            text_size=self.VMS_LENGTH_MAX,
            on_change=self.on_change_vms,
        )
        self.btnNext = ft.FilledButton(
            '次へ', on_click=self.on_click_next,
            disabled=False if 'target_vms' in self.session.get('job_options') else True)
        self.btnPrev = ft.ElevatedButton(
            '戻る', on_click=self.on_click_previous)
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
                self.dropCluster,
                self.tfVms,
            ],
            height=self.body_height,
        )
        footer = ft.Row(
            [
                self.btnCancel,
                self.btnPrev,
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
    def on_change_vms(self, e):
        if e.control.value == '':
            self.btnNext.disabled = True
        else:
            self.btnNext.disabled = False
        self.btnNext.update()

    @Logging.func_logger
    def on_click_cancel(self, e):
        self.step_change_cancel(e)

    @Logging.func_logger
    def on_click_previous(self, e):
        self.step_change_previous(e)

    @Logging.func_logger
    def on_click_next(self, e):
        self.session.get('job_options')[
            'vsphere_cluster'] = self.dropCluster.value
        self.session.get('job_options')['target_vms'] = self.tfVms.value
        self.step_change_next(e)
