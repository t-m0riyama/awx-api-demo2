import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle


class SessionTimeoutConfirmForm(ft.Card):
    """セッションタイムアウト フォーム"""

    # const
    CONTENT_HEIGHT = 200
    CONTENT_WIDTH = 500
    BODY_HEIGHT = 100

    def __init__(self, session, page: ft.Page):
        self.session = session
        self.page = page

        # controls
        formTitle = FormTitle('セッションのタイムアウト', None)
        formDescription = FormDescription(
            'セッションの有効期限が切れました。作業中の操作は保存されません。再度、ログイン後操作を行なって下さい。')

        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
            ],
            height=self.BODY_HEIGHT,
        )

        controls = ft.Container(
            ft.Column(
                [
                    header,
                    body,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=self.CONTENT_WIDTH,
            height=self.CONTENT_HEIGHT,
            padding=30,
        )

        super().__init__(controls)
