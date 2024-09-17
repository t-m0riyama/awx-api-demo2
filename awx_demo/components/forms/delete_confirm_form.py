import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle


class DeleteConfirmForm(ft.Card):
    """申請の削除 フォーム"""

    # const
    CONTENT_HEIGHT = 200
    CONTENT_WIDTH = 500
    BODY_HEIGHT = 100

    def __init__(self, session, page: ft.Page):
        self.session = session
        self.page = page

        # controls
        formTitle = FormTitle('削除の確認', None)
        formDescription = FormDescription(
            '選択した申請の削除を行います。削除処理を続ける場合は「はい」、中止する場合は「キャンセル」を選択して下さい。')

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
