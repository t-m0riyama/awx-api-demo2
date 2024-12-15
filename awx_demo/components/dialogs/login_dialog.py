import os

import flet as ft

from awx_demo.components.forms.login_form import LoginForm


class LoginDialog(ft.AlertDialog):
    """Login Dialog"""

    # const
    DEFAULT_AWX_URL = 'https://awx.example.com'

    def __init__(self, session, page: ft.Page):
        self.session = session
        self.page = page
        self.default_awx_url = os.getenv('RMX_AWX_URL', self.DEFAULT_AWX_URL)

        # controls
        formLogin = LoginForm(
            session=self.session, page=self.page, default_awx_url=self.default_awx_url)
        super().__init__(
            modal=True,
            # title=ft.Text("Login"),
            content=formLogin,
            # actions=[ft.TextButton("Cancel", on_click=close_login)],
        )
