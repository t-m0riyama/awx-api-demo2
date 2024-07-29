import flet as ft

from awx_demo.components.forms.create_request_form import CreateRequestForm
from awx_demo.components.wizards.set_vm_cpu_memory_wizard import SetVmCpuMemoryWizard
from awx_demo.utils.logging import Logging


class NewRequestWizard:

    # const
    CONTENT_HEIGHT = 540
    CONTENT_WIDTH = 800
    BODY_HEIGHT = 290

    def __init__(self, session, page: ft.Page, parent_refresh_func):
        self.session = session
        self.page = page
        self.parent_refresh_func = parent_refresh_func
        super().__init__()

    @Logging.func_logger
    def open_wizard(self):
        self.session.set("new_request_wizard_step", "create_request")
        formStep = CreateRequestForm(
            session=self.session,
            page=self.page,
            height=self.CONTENT_HEIGHT,
            width=self.CONTENT_WIDTH,
            body_height=self.BODY_HEIGHT,
            step_change_next=self.on_click_next,
            step_change_previous=self.on_click_previous,
            step_change_cancel=self.on_click_cancel,
        )
        self.wizard_dialog = ft.AlertDialog(
            modal=True,
            # title=ft.Text("削除の確認"),
            content=formStep,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.open(self.wizard_dialog)
        self.wizard_dialog.open = True
        self.page.update()

    @Logging.func_logger
    def on_click_cancel(self, e):
        if self.session.contains_key("job_options"):
            self.session.remove("job_options")
        self.wizard_dialog.open = False
        self.page.update()

    @Logging.func_logger
    def on_click_next(self, e):
        match self.session.get("new_request_wizard_step"):
            case "create_request":
                match self.session.get("request_operation"):
                    case "CPUコア/メモリ割り当て変更":
                        child_wizard = SetVmCpuMemoryWizard(
                            self.session,
                            self.page,
                            self.wizard_dialog,
                            self.parent_refresh_func,
                        )
                        child_wizard.on_click_next(e)
                    case _:
                        Logging.error("undefined operation!!!")
            case _:
                Logging.error("undefined step!!!")
        self.page.update()

    @Logging.func_logger
    def on_click_previous(self, e):
        match self.session.get("new_request_wizard_step"):
            case _:
                Logging.error("undefined step!!!")
        self.page.update()
