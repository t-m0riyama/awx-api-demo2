import flet as ft

from awx_demo.components.forms.base_activity_list_form import BaseActivityListForm
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.utils.event_helper import EventType
from awx_demo.utils.logging import Logging


class AllActivityListForm(BaseActivityListForm):

    # const
    DEFAULT_SORT_TARGET_COLUMN = "時刻"
    DEFAULT_SORT_COLUMN_INDEX = 1
    DEFAULT_SORT_ASCENDING = False
    FORM_TITLE = "操作履歴"

    def __init__(self, session, page: ft.Page):
        super().__init__(session, page)
        self.session.set("sort_target_column", self.DEFAULT_SORT_TARGET_COLUMN)

    @Logging.func_logger
    def get_query_filters(self):
        filters = []
        filters.append(ActivityHelper.get_filter_summary(self.session.get("request_text_search_string")))
        if (
            self.session.get("filter_activity_user") != ""
            and self.session.get("filter_activity_user") != "すべてのユーザ"
        ):
            filters.append(ActivityHelper.get_filter_user(self.session.get("filter_activity_user")))
        if self.session.get("filter_activity_type") and self.session.get("filter_activity_type") != "すべての操作":
            filters.append(
                ActivityHelper.get_filter_activity_type(EventType.to_formal(self.session.get("filter_activity_type")))
            )
        return filters
