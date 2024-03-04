import flet as ft

from awx_demo.db import db
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.db_helper.types.activity_type import ActivityStatus, ActivityType


class ActivityRowData():

    def __init__(self,  user, created, activity_type, status, summary, detail):
        self.user = user
        self.created = created
        self.activity_type = activity_type
        self.status = status
        self.summary = summary
        self.detail = detail


class ActivityRowHelper():

    @staticmethod
    def generate_activity_row(activity_list_form, id, activity_data: ActivityRowData):
        return ft.DataRow(
            cells=[
                ft.DataCell(ActivityRowHelper._activity_status_to_icon(
                    activity_data.status)),
                ft.DataCell(ft.Text(str(activity_data.created))),
                ft.DataCell(ft.Text(activity_data.user)),
                ft.DataCell(ft.Text(activity_data.activity_type)),
                ft.DataCell(ft.Text(str(id))),
                ft.DataCell(ft.Text(activity_data.summary)),
            ],
            # on_select_changed=activity_list_form.on_request_row_select,
        )

    @staticmethod
    def _activity_status_to_icon(activity_status):
        match activity_status:
            case ActivityStatus.SUCCEED:
                return ft.Icon(name=ft.icons.CHECK_CIRCLE, color=ft.colors.PRIMARY, tooltip=ActivityStatus.SUCCEED_FRIENDLY)
            case ActivityStatus.FAILED:
                return ft.Icon(name=ft.icons.ERROR_OUTLINED, color=ft.colors.ERROR, tooltip=ActivityStatus.FAILED_FRIENDLY)
            case ActivityStatus.UNKNOWN:
                return ft.Icon(name=ft.icons.QUESTION_MARK, color=ft.colors.PRIMARY, tooltip=ActivityStatus.UNKNOWN_FRIENDLY)

    @staticmethod
    def refresh_data_rows(activity_list_form):
        activities_data = ActivityRowHelper.query_activity_all(
            activity_list_form)
        activity_list_form.dtActivities.rows = []
        for activity_data in activities_data:
            activity_row_data = ActivityRowData(
                user=activity_data.user,
                created=activity_data.created.strftime('%Y/%m/%d %H:%M'),
                activity_type=ActivityType.to_friendly(
                    activity_data.activity_type),
                status=activity_data.status,
                summary=activity_data.summary,
                detail=activity_data.detail,
            )
            activity_list_form.dtActivities.rows.append(
                ActivityRowHelper.generate_activity_row(
                    activity_list_form,
                    activity_data.request_id,
                    activity_row_data,
                )
            )
        activity_list_form.dtActivities.update()

    @staticmethod
    def refresh_page_indicator(activity_list_form):
        range_min, range_max, request_data_count = ActivityRowHelper.get_page_range(
            activity_list_form)
        activity_list_form.textRequestsRange.value = "{}-{} / {}".format(
            range_min, range_max, request_data_count)
        activity_list_form.textRequestsRange.update()

        if (activity_list_form.data_row_offset + 1 + activity_list_form.DATA_ROW_MAX) >= request_data_count:
            activity_list_form.btnNextPage.disabled = True
            activity_list_form.btnNextPage.icon_color = ft.colors.ON_INVERSE_SURFACE
        else:
            activity_list_form.btnNextPage.disabled = False
            activity_list_form.btnNextPage.icon_color = ft.colors.ON_SURFACE_VARIANT
        activity_list_form.btnNextPage.update()

        if (activity_list_form.data_row_offset + 1 - activity_list_form.DATA_ROW_MAX) < 0:
            activity_list_form.btnPreviousPage.disabled = True
            activity_list_form.btnPreviousPage.icon_color = ft.colors.ON_INVERSE_SURFACE
        else:
            activity_list_form.btnPreviousPage.disabled = False
            activity_list_form.btnPreviousPage.icon_color = ft.colors.ON_SURFACE_VARIANT
        activity_list_form.btnPreviousPage.update()

    @staticmethod
    def get_page_range(activity_list_form):
        record_count = ActivityRowHelper.count_activity_all(activity_list_form)
        range_min = 0 if record_count == 0 else (
            activity_list_form.data_row_offset + 1)
        if (activity_list_form.data_row_offset + activity_list_form.DATA_ROW_MAX) <= record_count:
            range_max = activity_list_form.data_row_offset + activity_list_form.DATA_ROW_MAX
        else:
            range_max = record_count
        return range_min, range_max, record_count

    @staticmethod
    def query_activity_all(activity_list_form):
        db_session = db.get_db()
        activities_data = None
        filters = activity_list_form.get_query_filters()
        match activity_list_form.session.get('sort_target_column'):
            case '時刻':
                orderspec = ActivityHelper.get_orderspec_created(
                    activity_list_form.dtActivities.sort_ascending)
            case 'ユーザ名':
                orderspec = ActivityHelper.get_orderspec_user(
                    activity_list_form.dtActivities.sort_ascending)
            case '操作種別':
                orderspec = ActivityHelper.get_orderspec_activity_type(
                    activity_list_form.dtActivities.sort_ascending)
            case '依頼ID':
                orderspec = ActivityHelper.get_orderspec_request_id(
                    activity_list_form.dtActivities.sort_ascending)
            case '概要':
                orderspec = ActivityHelper.get_orderspec_summary(
                    activity_list_form.dtActivities.sort_ascending)

        activities_data = ActivityHelper.get_activities(
            db_session=db_session,
            filters=filters,
            orderspec=orderspec,
            offset_row=activity_list_form.data_row_offset,
            limit_rows=activity_list_form.DATA_ROW_MAX
        )
        db_session.close
        return activities_data

    @staticmethod
    def count_activity_all(activity_list_form):
        db_session = db.get_db()
        filters = activity_list_form.get_query_filters()
        activities_data = ActivityHelper.count_activities(db_session, filters)
        db_session.close
        return activities_data

    @staticmethod
    def sort_column(activity_list_form, session, column_lubel):
        session.set('sort_target_column', column_lubel)
        # ソート対象が同じ列の場合、昇順と降順を逆転させる
        if session.get('sort_target_column') == session.get('sort_target_column_old') \
                or not session.get('sort_target_column_old'):
            activity_list_form.dtActivities.sort_ascending = not activity_list_form.dtActivities.sort_ascending

        match column_lubel:
            case '時刻':
                activity_list_form.dtActivities.sort_column_index = 1
            case 'ユーザ名':
                activity_list_form.dtActivities.sort_column_index = 2
            case '操作種別':
                activity_list_form.dtActivities.sort_column_index = 3
            case '依頼ID':
                activity_list_form.dtActivities.sort_column_index = 4
            case '概要':
                activity_list_form.dtActivities.sort_column_index = 5
        session.set('sort_target_column_old', column_lubel)
        ActivityRowHelper.refresh_data_rows(activity_list_form)
