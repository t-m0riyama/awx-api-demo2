import json

import flet as ft

from awx_demo.components.forms.edit_request_form import EditRequestForm
from awx_demo.components.forms.job_execute_confirm_form import JobExecuteConfirmForm
from awx_demo.components.forms.job_progress_form import JobProgressForm
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.utils.doc_id_utils import DocIdUtils
from awx_demo.utils.logging import Logging


class EditRequestWizard:

    # const
    CONTENT_HEIGHT = 540
    CONTENT_WIDTH = 800
    BODY_HEIGHT = 370
    CONFIRM_FORM_TITLE = "ジョブ実行の確認"
    DUCUMENT_ID_LENGTH = 7

    def __init__(self, session, page: ft.Page, parent_refresh_func):
        self.session = session
        self.page = page
        self.parent_refresh_func = parent_refresh_func
        super().__init__()

    def open_wizard(self):
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
        self.wizard_dialog = ft.AlertDialog(
            modal=True,
            # title=ft.Text("削除の確認"),
            content=formStep,
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = self.wizard_dialog
        self.wizard_dialog.open = True
        self.page.update()

    def _duplicate_request(self):
        db_session = db.get_db()
        IaasRequestHelper.duplicate_request(
            db_session=db_session,
            request_id=self.session.get("request_id"),
            new_request_id=DocIdUtils.generate_id(self.DUCUMENT_ID_LENGTH),
            session=self.session,
        )
        db_session.close()

    def _update_request(self):
        db_session = db.get_db()
        IaasRequestHelper.update_request(
            db_session=db_session,
            request_id=self.session.get("request_id"),
            request_deadline=self.session.get("request_deadline"),
            request_text=self.session.get("request_text"),
            job_options=json.dumps(self.session.get("job_options")),
            request_status=self.session.get("request_status"),
            iaas_user=self.session.get("iaas_user"),
            session=self.session,
        )
        db_session.close()

    def on_click_next(self, e):
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
                self._update_request()
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
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
                self.wizard_dialog.content = formStep
                self.page.dialog = self.wizard_dialog
            case _:
                Logging.error("undefined step!!!")
        self.page.update()

    def on_click_previous(self, e):
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
                self.page.dialog = self.wizard_dialog
            case _:
                Logging.error("undefined step!!!")
        self.page.update()

    def on_click_save(self, e):
        self._update_request()
        self.wizard_dialog.open = False
        self.page.update()
        self.parent_refresh_func()

    def on_click_duplicate(self, e):
        self._duplicate_request()
        self.wizard_dialog.open = False
        self.page.update()
        self.parent_refresh_func()

    def on_click_cancel(self, e):
        self.session.remove("job_options")
        self.wizard_dialog.open = False
        self.page.update()
        self.parent_refresh_func()
