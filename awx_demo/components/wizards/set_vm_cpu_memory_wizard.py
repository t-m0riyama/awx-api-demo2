import flet as ft

from awx_demo.components.forms.create_request_form import CreateRequestForm
from awx_demo.components.forms.job_progress_form import JobProgressForm
from awx_demo.components.forms.select_target_form import SelectTargetForm
from awx_demo.components.forms.send_request_confirm_form import SendRequestConfirmForm
from awx_demo.components.forms.set_vm_cpu_form import SetVmCpuForm
from awx_demo.components.forms.set_vm_memory_form import SetVmMemoryForm
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.wizards.base_wizard import BaseWizard
from awx_demo.utils.logging import Logging


class SetVmCpuMemoryWizard(BaseWizard):

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

    @Logging.func_logger
    def on_click_next(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
        match self.session.get("new_request_wizard_step"):
            case "create_request":
                self.session.set("new_request_wizard_step", "select_target")
                formStep = SelectTargetForm(
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
                self.page.title = f"{self.session.get('app_title_base')} - 変更対象の選択"
                self.page.open(self.wizard_dialog)
            case "select_target":
                self.session.set("new_request_wizard_step", "set_vm_cpu")
                formStep = SetVmCpuForm(
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
                self.page.title = f"{self.session.get('app_title_base')} - CPUの割り当て変更"
                self.page.open(self.wizard_dialog)
            case "set_vm_cpu":
                self.session.set("new_request_wizard_step", "set_vm_memory")
                formStep = SetVmMemoryForm(
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
                self.page.title = f"{self.session.get('app_title_base')} - メモリの割り当て変更"
                self.page.open(self.wizard_dialog)
            case "set_vm_memory":
                self.session.set("new_request_wizard_step", "send_request_confirm")
                formStep = SendRequestConfirmForm(
                    session=self.session,
                    page=self.page,
                    title=self.CONFIRM_FORM_TITLE,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.title = f"{self.session.get('app_title_base')} - 変更内容の確認"
                self.page.open(self.wizard_dialog)
            case "send_request_confirm":
                if self.session.get("execute_job_immediately"):
                    self.session.set("new_request_wizard_step", "job_progress")
                    formStep = JobProgressForm(
                        session=self.session,
                        page=self.page,
                        request_id=self.session.get("request_id"),
                        height=self.CONTENT_HEIGHT,
                        width=self.CONTENT_WIDTH,
                        body_height=self.BODY_HEIGHT,
                        step_change_exit=self.on_click_cancel,
                    )
                    self.wizard_dialog.content = formStep
                    self.page.title = f"{self.session.get('app_title_base')} - 処理の進捗"
                    self.page.open(self.wizard_dialog)
                else:
                    self.wizard_dialog.open = False
                    self.parent_refresh_func()
                    self.restore_parent_view_title()
                    self.page.update()
            case _:
                Logging.error("undefined step!!!")

        self.page.update()

    @Logging.func_logger
    def on_click_previous(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
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
                self.page.title = f"{self.session.get('app_title_base')} - 申請の追加"
                self.page.open(self.wizard_dialog)
            case "set_vm_cpu":
                self.session.set("new_request_wizard_step", "select_target")
                formStep = SelectTargetForm(
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
                self.page.title = f"{self.session.get('app_title_base')} - 変更対象の選択"
                self.page.open(self.wizard_dialog)
            case "set_vm_memory":
                self.session.set("new_request_wizard_step", "set_vm_cpu")
                formStep = SetVmCpuForm(
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
                self.page.title = f"{self.session.get('app_title_base')} - CPUの割り当て変更"
                self.page.open(self.wizard_dialog)
            case "send_request_confirm":
                self.session.set("new_request_wizard_step", "set_vm_memory")
                formStep = SetVmMemoryForm(
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
                self.page.title = f"{self.session.get('app_title_base')} - メモリの割り当て変更"
                self.page.open(self.wizard_dialog)
            case _:
                Logging.error("undefined step!!!")
        self.page.update()
