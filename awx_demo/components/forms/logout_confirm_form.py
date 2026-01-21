import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle


class LogoutConfirmForm(ft.Card):
    """ログアウト確認 フォーム"""

    # const
    CONTENT_HEIGHT = 200
    CONTENT_WIDTH = 500
    BODY_HEIGHT = 100

    def __init__(
        self,
        session,
        page: ft.Page,
        description: str = "アプリケーションにエラーが発生しました。ログイン後に再度操作を行なって下さい。",
    ):
        self.session = session
        self.page = page
        self.description = description

        # controls
        formTitle = FormTitle("ログアウトの確認", None)
        formDescription = FormDescription(self.description)

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
