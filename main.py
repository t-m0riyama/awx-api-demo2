import os

import flet as ft

from awx_demo.components.forms.login_form import LoginForm
from awx_demo.components.navigation_router import NavigationRouter
from awx_demo.utils.logging import Logging

# const
FLET_PATH_DEFAULT = "app"
FLET_PORT_DEFAULT = 8888
APP_TITLE_DEFAULT = "AWX API Demo"
LOG_DIR_DEFAULT = "./log"
LOG_FILE_DEFAULT = "awx_api_demo2.log"

def main(page: ft.Page):

    def route_change(e):
        router = NavigationRouter(page.session, page, app_title, dlgLogin)
        router.route_change()

    app_title = os.getenv("RMX_APP_TITLE", APP_TITLE_DEFAULT).strip('"')
    formLogin = LoginForm(session=page.session, page=page)
    dlgLogin = ft.AlertDialog(
        modal=True,
        content=formLogin,
    )

    # Page レイアウト
    page.title = app_title
    page.padding = 10
    page.window.height = 720
    page.window.width = 1120
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.on_route_change = route_change
    page.theme_mode = "light"

    # Locale Settings
    page.locale_configuration = ft.LocaleConfiguration(
        supported_locales=[
            ft.Locale("ja", "JP"),
            ft.Locale("en", "US")
        ],
        current_locale=ft.Locale("ja", "JP")
    )

    # Add Dialog
    page.overlay.append(dlgLogin)

    # Show dialog
    dlgLogin.open = True
    page.update()


if __name__ == "__main__":
    log_dir = os.getenv("RMX_LOG_DIR", LOG_DIR_DEFAULT)
    log_file = os.getenv("RMX_LOG_FILE", LOG_FILE_DEFAULT)
    Logging.init(log_dir, log_file)
    flet_path = os.getenv("FLET_PATH", FLET_PATH_DEFAULT)
    flet_port = int(os.getenv("FLET_PORT", FLET_PORT_DEFAULT))
    # ft.app(target=main, port=flet_port, view=ft.AppView.FLET_APP)
    ft.app(target=main, port=flet_port, view=ft.AppView.WEB_BROWSER)
