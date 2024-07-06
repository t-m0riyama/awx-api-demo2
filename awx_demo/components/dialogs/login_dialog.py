import os

import flet as ft

from awx_demo.components.forms.login_form import LoginForm


class LoginDialog(ft.UserControl):
    """Login Dialog"""

    # const
    DEFAULT_AWX_URL = 'https://awx.example.com'

    def __init__(self, session, page: ft.Page):
        self.session = session
        self.page = page
        self.default_awx_url = os.getenv('RMX_AWX_URL', self.DEFAULT_AWX_URL)
        # formLogin = LoginForm(session=session, page=page, default_awx_url=default_awx_url)
        # controls = [
        #                 formLogin,
        #            ]
        # super().__init__(
        #     route='/login',
        #     horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        #     vertical_alignment=ft.MainAxisAlignment.CENTER,
        #     controls=controls
        # )
        super().__init__()

    def build(self):
        formLogin = LoginForm(
            session=self.session, page=self.page, default_awx_url=self.default_awx_url)
        return ft.AlertDialog(
            modal=True,
            # title=ft.Text("Login"),
            content=formLogin,
            # actions=[ft.TextButton("Cancel", on_click=close_login)],
        )
