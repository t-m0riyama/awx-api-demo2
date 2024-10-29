import flet as ft

from awx_demo.components.forms.edit_request_form import EditRequestForm
from awx_demo.components.forms.job_execute_confirm_form import JobExecuteConfirmForm
from awx_demo.components.forms.job_progress_form import JobProgressForm
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.wizards.base_wizard import BaseWizard
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.utils.logging import Logging


class EditRequestWizard(BaseWizard):

    # const
    CONTENT_HEIGHT = 540
    CONTENT_WIDTH = 800
    BODY_HEIGHT = 370
    CONFIRM_FORM_TITLE = "ジョブ実行の確認"
    DOCUMENT_ID_LENGTH = 7

    def __init__(self, session, page: ft.Page, parent_refresh_func):
        self.session = session
        self.page = page
        self.parent_refresh_func = parent_refresh_func
        db_session = db.get_db()
        request_operation = IaasRequestHelper.get_request(db_session, self.session.get("request_id")).request_operation
        Logging.warning(f"job_options: {request_operation}")
        db_session.close()
        formStep = EditRequestForm(
            session=self.session,
            page=self.page,
            request_id=self.session.get("request_id"),
            height=self.CONTENT_HEIGHT,
            width=self.CONTENT_WIDTH,
            body_height=self.BODY_HEIGHT,
            click_execute_func=self.on_click_next,
            click_save_func=self.on_click_save,
            click_duplicate_func=self.on_click_duplicate,
            click_cancel_func=self.on_click_cancel,
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
        self.session.set("edit_request_wizard_step", "edit_request")
        self.save_parent_view_title()
        self.page.open(self.wizard_dialog)
        self.wizard_dialog.open = True
        self.page.title = f"{self.session.get('app_title_base')} - 申請の編集"
        self.page.update()

    @Logging.func_logger
    def on_click_next(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
        match self.session.get("edit_request_wizard_step"):
            case "edit_request":
                self.session.set("edit_request_wizard_step", "job_execute_confirm")
                formStep = JobExecuteConfirmForm(
                    session=self.session,
                    title=self.CONFIRM_FORM_TITLE,
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT - 70,
                    step_change_next=self.on_click_next,
                    step_change_previous=self.on_click_previous,
                    step_change_cancel=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.title = f"{self.session.get('app_title_base')} - 変更内容の確認"
                self.page.open(self.wizard_dialog)
            case "job_execute_confirm":
                self.session.set("edit_request_wizard_step", "job_progress")
                formStep = JobProgressForm(
                    session=self.session,
                    request_id=self.session.get("request_id"),
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT - 70,
                    step_change_exit=self.on_click_cancel,
                )
                self._update_request()
                self.wizard_dialog.content = formStep
                self.page.title = f"{self.session.get('app_title_base')} - 処理の進捗"
                self.page.open(self.wizard_dialog)
            case _:
                Logging.error(f'undefined step: {self.session.get("edit_request_wizard_step")}')
        self.page.update()

    @Logging.func_logger
    def on_click_previous(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
        match self.session.get("edit_request_wizard_step"):
            case "job_execute_confirm":
                self.session.set("edit_request_wizard_step", "edit_request")
                formStep = EditRequestForm(
                    session=self.session,
                    page=self.page,
                    request_id=self.session.get("request_id"),
                    height=self.CONTENT_HEIGHT,
                    width=self.CONTENT_WIDTH,
                    body_height=self.BODY_HEIGHT,
                    click_execute_func=self.on_click_next,
                    click_save_func=self.on_click_save,
                    click_duplicate_func=self.on_click_duplicate,
                    click_cancel_func=self.on_click_cancel,
                )
                self.wizard_dialog.content = formStep
                self.page.title = f"{self.session.get('app_title_base')} - 申請の編集"
                self.page.open(self.wizard_dialog)
            case _:
                Logging.error(f'undefined step: {self.session.get("edit_request_wizard_step")}')
        self.page.update()
