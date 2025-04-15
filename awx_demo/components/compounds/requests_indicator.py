import flet as ft

from awx_demo.utils.logging import Logging


class RequestsIndicator(ft.Container):

    # const
    CONTENT_WIDTH = 130
    TITLE_FONT_SIZE_LARGE = 18
    TITLE_FONT_SIZE_MEDIUM = 14
    TITLE_FONT_SIZE_SMALL = 12
    REQUESTS_COUNT_FONT_SIZE_LARGE = 64
    REQUESTS_COUNT_FONT_SIZE_MEDIUM = 52
    REQUESTS_COUNT_FONT_SIZE_SMALL = 36
    ICON_SIZE = 28
    BORDER_WIDTH_DEFAULT=2
    BORDER_COLOR_DEFAULT=ft.Colors.SURFACE_CONTAINER_HIGHEST

    def __init__(
        self,
        title: str,
        title_font_size=TITLE_FONT_SIZE_MEDIUM,
        indicator_text: str='',
        indicator_text_font_size=REQUESTS_COUNT_FONT_SIZE_MEDIUM,
        icon: ft.Icon=ft.Icon(ft.Icons.FIBER_NEW, size=ICON_SIZE),
        border_width=BORDER_WIDTH_DEFAULT,
        border_color=BORDER_COLOR_DEFAULT,
        on_click=None,
        tooltip='',
    ):
        self.title = title
        self.title_font_size = title_font_size
        self.indicator_text = indicator_text
        self.requests_count_font_size = indicator_text_font_size
        self.icon = icon
        self.indicator_body = ft.Text(
            value=self.indicator_text,
            # theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
            size=self.requests_count_font_size,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.ON_SECONDARY,
            text_align=ft.TextAlign.CENTER,
            tooltip=tooltip,
        )
        self.controls = ft.Container(
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            border=ft.border.all(border_width, border_color),
            border_radius=ft.border_radius.all(5),
            content=ft.Column(
                [
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=icon,
                                # bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                padding=ft.padding.only(left=5, top=5),
                            ),
                            ft.Container(
                                ft.Text(
                                    value=self.title,
                                    # theme_style=ft.TextThemeStyle.DISPLAY_MEDIUM,
                                    size=self.title_font_size,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.ON_SURFACE_VARIANT,
                                    text_align=ft.TextAlign.START,
                                ),
                                # col={"sm": 12},
                                # bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
                                padding=ft.padding.only(left=0, top=5),
                                expand=True,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.VerticalAlignment.CENTER,
                        expand=True,
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                self.indicator_body,
                                # col={"sm": 12},
                                bgcolor=ft.Colors.SECONDARY,
                                expand=True,
                                padding=ft.padding.all(5),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.VerticalAlignment.CENTER,
                        expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                # expand=True,
                width=self.CONTENT_WIDTH,
            ),
        )
        # super().__init__(controls=[self.body])
        super().__init__(self.controls, on_click=on_click, margin=ft.margin.all(0))

    @Logging.func_logger
    def set_indicator_text(self, indicator_text):
        self.indicator_text = indicator_text
        self.indicator_body.value = self.indicator_text

    @Logging.func_logger
    def set_border(self, width=BORDER_WIDTH_DEFAULT, color=BORDER_COLOR_DEFAULT):
        self.controls.border = ft.border.all(width, color)
