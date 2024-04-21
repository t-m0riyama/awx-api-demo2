import logging
import os

import flet as ft

from awx_demo.components.forms.login_form import LoginForm
from awx_demo.components.navigation_router import NavigationRouter

# const
DEFAULT_FLET_PATH = "app"
DEFAULT_FLET_PORT = 8888
APP_TITLE = "AWX API Demo"
LOG_DIR = "./log"
LOG_FILE = "awx_api_demo2.log"

def main(page: ft.Page):

    def route_change(e):
        router = NavigationRouter(page.session, page, APP_TITLE, dlgLogin)
        router.route_change()

    formLogin = LoginForm(session=page.session, page=page)
    dlgLogin = ft.AlertDialog(
        modal=True,
        content=formLogin,
    )

    # Page レイアウト
    page.title = APP_TITLE
    page.padding = 10
    page.window_height = 720
    page.window_width = 1120
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.on_route_change = route_change
    page.theme_mode = "light"

    # Add Dialog
    page.dialog = dlgLogin

    # Show dialog
    dlgLogin.open = True
    page.update()


if __name__ == "__main__":
    logging.basicConfig(
        filename='{}/{}'.format(LOG_DIR, LOG_FILE),
        format="\"%(asctime)s\"\t%(levelname)s\t%(message)s",
        datefmt='%Y/%m/%d %H:%M:%S',
        level=logging.INFO,
    )
    flet_path = os.getenv("FLET_PATH", DEFAULT_FLET_PATH)
    flet_port = int(os.getenv("FLET_PORT", DEFAULT_FLET_PORT))
    # ft.app(name=flet_path, target=main, port=flet_port, view=None)
    ft.app(target=main, port=flet_port, view=ft.WEB_BROWSER)
