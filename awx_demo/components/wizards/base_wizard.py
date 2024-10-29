import abc
import json

from awx_demo.components.session_helper import SessionHelper
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.utils.doc_id_utils import DocIdUtils
from awx_demo.utils.logging import Logging


class BaseWizard(metaclass=abc.ABCMeta):

    # const
    CONTENT_HEIGHT = 540
    CONTENT_WIDTH = 800
    BODY_HEIGHT = 290

    @Logging.func_logger
    def _duplicate_request(self):
        db_session = db.get_db()
        IaasRequestHelper.duplicate_request(
            db_session=db_session,
            request_id=self.session.get("request_id"),
            new_request_id=DocIdUtils.generate_id(self.DOCUMENT_ID_LENGTH),
            session=self.session,
        )
        db_session.close()

    @Logging.func_logger
    def _update_request(self):
        if self.session.get("iaas_user") is None:
            self.session.set("iaas_user", self.session.get("awx_loginid"))
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

    @Logging.func_logger
    def save_parent_view_title(self):
        self.session.set("parent_view_title", self.page.title)

    @Logging.func_logger
    def restore_parent_view_title(self):
        self.page.title = self.session.get("parent_view_title")

    @Logging.func_logger
    def on_click_cancel(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
        if self.session.contains_key("job_options"):
            self.session.remove("job_options")
        self.wizard_dialog.open = False
        self.restore_parent_view_title()
        self.page.update()
        self.parent_refresh_func()

    @Logging.func_logger
    def on_click_save(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
        self._update_request()
        self.wizard_dialog.open = False
        self.restore_parent_view_title()
        self.page.update()
        self.parent_refresh_func()

    @Logging.func_logger
    def on_click_duplicate(self, e):
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.wizard_dialog): return
        self._duplicate_request()
        self.wizard_dialog.open = False
        self.restore_parent_view_title()
        self.page.update()
        self.parent_refresh_func()

    @abc.abstractmethod
    def on_click_next(self, e):
        pass

    @abc.abstractmethod
    def on_click_previous(self, e):
        pass
