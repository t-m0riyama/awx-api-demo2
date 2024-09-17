import json

import flet as ft

from awx_demo.components.forms.session_timeout_confirm_form import SessionTimeoutConfirmForm
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.utils.logging import Logging


class SessionHelper:

    @classmethod
    @Logging.func_logger
    def clean_session(cls, session):
        cls.clean_request_from_session(session)
        cls.clean_wizard_steps(session)
        cls._remove_session_key(session, "awx_loginid")
        cls._remove_session_key(session, "awx_password")
        cls._remove_session_key(session, "user_role")
        cls._remove_session_key(session, "request_text_search_string")

    @staticmethod
    @Logging.func_logger
    def clean_wizard_steps(session):
        SessionHelper._remove_session_key(session, "edit_request_wizard_step")
        SessionHelper._remove_session_key(session, "new_request_wizard_step")

    @staticmethod
    @Logging.func_logger
    def dump_session(session):
        for session_key_name in session.get_keys():
            Logging.info(f"SESSION_DUMP / {session_key_name}: {session.get(session_key_name)}")

    @staticmethod
    @Logging.func_logger
    def clean_request_from_session(session):
        SessionHelper._remove_session_key(session, "request_date")
        SessionHelper._remove_session_key(session, "request_text")
        SessionHelper._remove_session_key(session, "request_category")
        SessionHelper._remove_session_key(session, "request_operation")
        SessionHelper._remove_session_key(session, "request_deadline")
        SessionHelper._remove_session_key(session, "request_status")
        SessionHelper._remove_session_key(session, "iaas_user")
        SessionHelper._remove_session_key(session, "job_id")
        SessionHelper._remove_session_key(session, "job_options")
        SessionHelper._remove_session_key(session, "updated")
        SessionHelper._remove_session_key(session, "document_id")
        SessionHelper._remove_session_key(session, "confirm_text")


    @staticmethod
    @Logging.func_logger
    def load_request_to_session_from_db(session, db_session, request_id):
        Logging.info("REQUEST_ID: " + request_id)
        session.set("document_id", request_id)
        request = IaasRequestHelper.get_request(db_session, request_id)
        session.set("request_date", request.request_date)
        session.set("request_text", request.request_text)
        session.set("request_category", request.request_category)
        session.set("request_operation", request.request_operation)
        session.set("request_deadline", request.request_deadline)
        session.set("request_status", request.request_status)
        session.set("iaas_user", request.iaas_user)
        if request.job_id:
            session.set("job_id", request.job_id)
        session.set("job_options", json.loads(request.job_options))
        session.set("updated", request.updated)

    @staticmethod
    @Logging.func_logger
    def is_valid_session(session):
        if session.contains_key("awx_loginid"):
            return True
        else:
            Logging.warning("SESSION_EXPIRED: awx_loginid is not set")
            return False

    @classmethod
    @Logging.func_logger
    def logout_if_session_expired(cls, page, session, old_dialog=None):
        def _logout(cls):
            page.close(dlgSessionTimeoutConfirm)
            page.go("/login")
            page.update()

        formSessionTimeoutConfirm = SessionTimeoutConfirmForm(session, page)
        dlgSessionTimeoutConfirm = ft.AlertDialog(
            modal=True,
            # title=ft.Text("セッションのタイムアウト"),
            content=formSessionTimeoutConfirm,
            actions=[
                ft.FilledButton("はい", on_click=_logout)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if not SessionHelper.is_valid_session(session):
            SessionHelper.clean_session(session)
            if old_dialog:
                old_dialog.open = False
            page.open(dlgSessionTimeoutConfirm)
            dlgSessionTimeoutConfirm.open = True
            page.update()
            return True
        else:
            return False

    @staticmethod
    @Logging.func_logger
    def _remove_session_key(session, key):
        if session.contains_key(key):
            session.remove(key)
