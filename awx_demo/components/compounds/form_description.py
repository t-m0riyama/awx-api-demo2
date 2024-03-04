import flet as ft


class FormDescription(ft.UserControl):

    def __init__(self, description):
        self.description = description
        super().__init__()

    def build(self):
        return ft.Text(
            value=self.description,
            theme_style=ft.TextThemeStyle.BODY_LARGE,
            text_align=ft.TextAlign.LEFT
        )
