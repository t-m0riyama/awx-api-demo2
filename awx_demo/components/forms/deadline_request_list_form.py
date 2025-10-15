import flet as ft

from awx_demo.components.forms.base_request_list_form import BaseRequestListForm
from awx_demo.components.types.user_role import UserRole
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class DeadlineRequestListForm(BaseRequestListForm):

    # const
    DEFAULT_SORT_TARGET_COLUMN = "リリース希望日"
    DEFAULT_SORT_COLUMN_INDEX = 3
    DEFAULT_SORT_ASCENDING = True
    FORM_TITLE = "リリース希望日順"

    def __init__(self, session, page: ft.Page):
        super().__init__(session, page)
        session.set("sort_target_column", self.DEFAULT_SORT_TARGET_COLUMN)

    @Logging.func_logger
    def get_query_filters(self):
        filters = []
        filters.append(IaasRequestHelper.get_filter_request_text(self.session.get("request_text_search_string")))
        filters.append(
            IaasRequestHelper.get_filter_request_status(
                [RequestStatus.APPROVED, RequestStatus.APPLYING, RequestStatus.APPLYING_FAILED, RequestStatus.START]
            )
        )
        if self.session.get("user_role") == UserRole.USER_ROLE:
            filters.append(IaasRequestHelper.get_filter_request_user(self.session.get("awx_loginid")))
        return filters
