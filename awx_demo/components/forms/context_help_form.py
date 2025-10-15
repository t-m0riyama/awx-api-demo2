import flet as ft

from awx_demo.components.compounds.form_title import FormTitle


class ContextHelpForm(ft.Card):
    """コンテキストヘルプ フォーム"""

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 520
    BODY_HEIGHT = 350

    def __init__(self, session, page: ft.Page, title: str, content_md: str):
        self.session = session
        self.page = page
        self.title = title
        help_content_md = ft.Markdown(
            content_md,
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            on_tap_link=lambda e: page.launch_url(e.data),
        )

        # controls
        formTitle = FormTitle(f"ヘルプ :    {self.title}", None, title_font_sizes=FormTitle.TITLE_FONT_SIZES_SMALL)
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                help_content_md,
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
