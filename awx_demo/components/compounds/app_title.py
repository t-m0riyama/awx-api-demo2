import flet as ft


class AppTitle(ft.Container):

    def __init__(self, title, width):
        super().__init__(
            ft.Text(
                title,
                theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.PRIMARY,
                width=width,
                text_align=ft.TextAlign.CENTER),
            margin=ft.margin.only(bottom=20),
        )
