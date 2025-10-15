import flet as ft

from awx_demo.components.forms.base_request_list_form import BaseRequestListForm
from awx_demo.components.types.user_role import UserRole
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.utils.logging import Logging


class AllRequestListForm(BaseRequestListForm):

    # const
    DEFAULT_SORT_TARGET_COLUMN = "最終更新日"
    DEFAULT_SORT_COLUMN_INDEX = 4
    DEFAULT_SORT_ASCENDING = False
    FORM_TITLE = "全ての申請"

    def __init__(self, session, page: ft.Page):
        super().__init__(session, page)
        session.set("sort_target_column", self.DEFAULT_SORT_TARGET_COLUMN)

    @Logging.func_logger
    def get_query_filters(self):
        filters = []
        filters.append(IaasRequestHelper.get_filter_request_text(self.session.get("request_text_search_string")))
        if self.session.get("user_role") == UserRole.USER_ROLE:
            filters.append(IaasRequestHelper.get_filter_request_user(self.session.get("awx_loginid")))
        return filters
