import flet as ft


class FormTitle(ft.Column):

    def __init__(self, title, sub_title, width):
        self.title = title
        self.sub_title = sub_title
        self.title_width = width
        controls = None
        if self.sub_title:
            controls =[
                ft.Container(
                    ft.Text(
                        value=self.title,
                        # theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SECONDARY,
                        width=self.title_width,
                        text_align=ft.TextAlign.CENTER
                    ),
                    bgcolor=ft.colors.SECONDARY,
                ),

                ft.Text(
                    value=self.sub_title,
                    # theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
                    size=24,
                    weight=ft.FontWeight.NORMAL,
                    width=self.title_width,
                    text_align=ft.TextAlign.CENTER
                ),
            ]
        else:
            controls = [
                ft.Container(
                    ft.Text(
                        value=self.title,
                        # theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                        size=30,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.ON_SECONDARY,
                        width=self.title_width,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    bgcolor=ft.colors.SECONDARY,
                    col={"sm": 12},
                ),
            ]
        super().__init__(controls=controls)
