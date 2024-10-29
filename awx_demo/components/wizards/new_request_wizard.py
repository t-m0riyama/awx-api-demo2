import flet as ft

from awx_demo.components.forms.create_request_form import CreateRequestForm
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.wizards.base_wizard import BaseWizard
from awx_demo.components.wizards.set_vm_cpu_memory_wizard import SetVmCpuMemoryWizard
from awx_demo.components.wizards.set_vm_start_stop_wizard import SetVmStartStopWizard
from awx_demo.db_helper.types.request_category import RequestOperation
from awx_demo.utils.logging import Logging


class NewRequestWizard(BaseWizard):

    # const
    CONTENT_HEIGHT = 540
    CONTENT_WIDTH = 800
    BODY_HEIGHT = 290

    def __init__(self, session, page: ft.Page, parent_refresh_func):
        self.session = session
        self.page = page
        self.parent_refresh_func = parent_refresh_func
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
        super().__init__()

    @Logging.func_logger
    def open_wizard(self):
        self.session.set("new_request_wizard_step", "create_request")
        self.save_parent_view_title()
        self.page.open(self.wizard_dialog)
        self.wizard_dialog.open = True
        self.page.title = f"{self.session.get('app_title_base')} - 申請の追加"
        self.page.update()

    @Logging.func_logger
    def on_click_next(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
        match self.session.get("new_request_wizard_step"):
            case "create_request":
                match self.session.get("request_operation"):
                    case RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY:
                        child_wizard = SetVmCpuMemoryWizard(
                            self.session,
                            self.page,
                            self.wizard_dialog,
                            self.parent_refresh_func,
                        )
                        child_wizard.on_click_next(e)
                    case RequestOperation.VM_START_OR_STOP_FRIENDLY:
                        child_wizard = SetVmStartStopWizard(
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
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
        match self.session.get("new_request_wizard_step"):
            case _:
                Logging.error("undefined step!!!")
        self.page.update()
