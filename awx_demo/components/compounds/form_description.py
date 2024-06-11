import flet as ft


class FormDescription(ft.Text):

    def __init__(self, description):
        super().__init__(
            value=description,
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            text_align=ft.TextAlign.LEFT
        )
