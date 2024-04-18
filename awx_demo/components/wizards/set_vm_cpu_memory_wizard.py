import flet as ft

from awx_demo.components.forms.create_request_form import CreateRequestForm
from awx_demo.components.forms.job_progress_form import JobProgressForm
from awx_demo.components.forms.select_target_form import SelectTargetForm
from awx_demo.components.forms.send_request_confirm_form import SendRequestConfirmForm
from awx_demo.components.forms.set_vm_cpu_form import SetVmCpuForm
from awx_demo.components.forms.set_vm_memory_form import SetVmMemoryForm


class SetVmCpuMemoryWizard:

    # const
    CONTENT_HEIGHT = 540
    CONTENT_WIDTH = 800
    BODY_HEIGHT = 290
    CONFIRM_FORM_TITLE = "CPU/メモリ割り当て変更"

    def __init__(
        self, session, page: ft.Page, wizard_dialog: ft.AlertDialog, parent_refresh_func
    ):
        self.session = session
        self.page = page
        self.wizard_dialog = wizard_dialog
        self.parent_refresh_func = parent_refresh_func
        super().__init__()

    def on_click_cancel(self, e):
        self.session.remove("job_options")
        self.wizard_dialog.open = False
        self.page.update()

    def on_click_next(self, e):
        match self.session.get("new_request_wizard_step"):
            case "create_request":
                self.session.set("new_request_wizard_step", "select_target")
                formStep = SelectTargetForm(
                    session=self.session,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case "select_target":
                self.session.set("new_request_wizard_step", "set_vm_cpu")
                formStep = SetVmCpuForm(
                    session=self.session,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case "set_vm_cpu":
                self.session.set("new_request_wizard_step", "set_vm_memory")
                formStep = SetVmMemoryForm(
                    session=self.session,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case "set_vm_memory":
                self.session.set("new_request_wizard_step", "send_request_confirm")
                formStep = SendRequestConfirmForm(
                    session=self.session,
                    title=self.CONFIRM_FORM_TITLE,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case "send_request_confirm":
                if self.session.get("execute_job_immediately"):
                    self.session.set("new_request_wizard_step", "job_progress")
                    formStep = JobProgressForm(
                        session=self.session,
                        height=self.CONTENT_HEIGHT,
                        width=self.CONTENT_WIDTH,
                        body_height=self.BODY_HEIGHT,
                        step_change_exit=self.on_click_next,
                    )
                    self.wizard_dialog.content = formStep
                    self.page.dialog = self.wizard_dialog
                else:
                    self.wizard_dialog.open = False
                    self.parent_refresh_func()
                    self.page.update()
            case _:
                print("undefined step!!!")

        self.page.update()

    def on_click_previous(self, e):
        match self.session.get("new_request_wizard_step"):
            case "select_target":
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
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case "set_vm_cpu":
                self.session.set("new_request_wizard_step", "select_target")
                formStep = SelectTargetForm(
                    session=self.session,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case "set_vm_memory":
                self.session.set("new_request_wizard_step", "set_vm_cpu")
                formStep = SetVmCpuForm(
                    session=self.session,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case "send_request_confirm":
                self.session.set("new_request_wizard_step", "set_vm_memory")
                formStep = SetVmMemoryForm(
                    session=self.session,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case _:
                print("undefined step!!!")
        self.page.update()
