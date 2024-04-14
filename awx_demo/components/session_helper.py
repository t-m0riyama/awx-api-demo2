import json

from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper


class SessionHelper:

    @staticmethod
    def clean_session(session):
        SessionHelper.clean_request_from_session(session)
        SessionHelper.clean_wizard_steps(session)
        session.remove("awx_loginid")
        session.remove("awx_password")
        session.remove("user_role")

    @staticmethod
    def clean_wizard_steps(session):
        if session.contains_key("edit_request_wizard_step"):
            session.remove("edit_request_wizard_step")
        if session.contains_key("new_request_wizard_step"):
            session.remove("new_request_wizard_step")

    @staticmethod
    def dump_session(session):
        for k in session.get_keys():
            print("SESSION_DUMP {}: {}".format(k, session.get(k)))

    @staticmethod
    def clean_request_from_session(session):
        if session.contains_key("request_id"):
            session.remove("request_id")
        if session.contains_key("request_date"):
            session.remove("request_date")
        if session.contains_key("request_text"):
            session.remove("request_text")
        if session.contains_key("request_category"):
            session.remove("request_category")
        if session.contains_key("request_operation"):
            session.remove("request_operation")
        if session.contains_key("request_deadline"):
            session.remove("request_deadline")
        if session.contains_key("request_status"):
            session.remove("request_status")
        if session.contains_key("iaas_user"):
            session.remove("iaas_user")
        if session.contains_key("job_id"):
            session.remove("job_id")
        if session.contains_key("job_options"):
            session.remove("job_options")
        if session.contains_key("updated"):
            session.remove("updated")
        if session.contains_key("document_id"):
            session.remove("document_id")
        if session.contains_key("confirm_text"):
            session.remove("confirm_text")

    @staticmethod
    def load_request_to_session_from_db(session, db_session, request_id):
        print("REQUEST_ID: " + request_id)
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
