import flet as ft


class FormTitle(ft.Column):

    def __init__(self, title, sub_title):
        self.title = title
        self.sub_title = sub_title
        controls = None
        if self.sub_title:
            controls = [
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            ft.Text(
                                value=self.title,
                                # theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                                size=30,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.ON_SECONDARY,
                                text_align=ft.TextAlign.CENTER
                            ),
                            col={"sm": 12},
                            bgcolor=ft.colors.SECONDARY,
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            ft.Text(
                                value=self.sub_title,
                                # theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
                                size=24,
                                weight=ft.FontWeight.NORMAL,
                                text_align=ft.TextAlign.CENTER
                            ),
                            col={"sm": 12},
                        ),
                    ],
                ),
            ]
        else:
            controls = [
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            ft.Text(
                                value=self.title,
                                # theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                                size=30,
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.ON_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            col={"sm": 12},
                            bgcolor=ft.colors.SECONDARY,
                        ),
                    ]
                )
            ]
        super().__init__(controls=controls)
