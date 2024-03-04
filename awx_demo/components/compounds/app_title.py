import flet as ft


class AppTitle(ft.UserControl):

    def __init__(self, title, width):
        self.title = title
        self.title_width = width
        super().__init__()

    def build(self):
        return ft.Container(
            ft.Text(
                self.title,
                theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.PRIMARY,
                width=self.title_width,
                text_align=ft.TextAlign.CENTER),
            margin=ft.margin.only(bottom=20),
        )
