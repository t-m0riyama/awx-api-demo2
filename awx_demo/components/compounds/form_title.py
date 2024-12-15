import flet as ft


class FormTitle(ft.Column):
    # const
    TITLE_FONT_SIZES_LARGE = (36, 30)
    TITLE_FONT_SIZES_MEDIUM = (30, 24)
    TITLE_FONT_SIZES_SMALL = (24, 18)

    def __init__(self, title, sub_title, title_font_sizes=TITLE_FONT_SIZES_MEDIUM):
        self.title = title
        self.sub_title = sub_title
        self.title_font_sizes = title_font_sizes
        controls = None
        if self.sub_title:
            controls = [
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            ft.Text(
                                value=self.title,
                                # theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                                size=self.title_font_sizes[0],
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_SECONDARY,
                                text_align=ft.TextAlign.CENTER
                            ),
                            col={"sm": 12},
                            bgcolor=ft.Colors.SECONDARY,
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    [
                        ft.Container(
                            ft.Text(
                                value=self.sub_title,
                                # theme_style=ft.TextThemeStyle.DISPLAY_SMALL,
                                size=self.title_font_sizes[1],
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
                                size=self.title_font_sizes[0],
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.ON_SECONDARY,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            col={"sm": 12},
                            bgcolor=ft.Colors.SECONDARY,
                        ),
                    ]
                )
            ]
        super().__init__(controls=controls)
