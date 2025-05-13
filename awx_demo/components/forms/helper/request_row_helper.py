import datetime
import json

import flet as ft

from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class RequestRowData:

    def __init__(self, request_status, request_deadline, updated, request_user, iaas_user, request_operation, request_text):
        self.request_status = request_status
        self.request_deadline = request_deadline
        self.updated = updated
        self.request_user = request_user
        self.iaas_user = iaas_user
        self.request_operation = request_operation
        self.request_text = request_text


class RequestRowHelper:

    # const
    REQUEST_ID_COLUMN_NUMBER = 2

    @staticmethod
    @Logging.func_logger
    def generate_request_row(request_list_form, row_id, request_data: RequestRowData, shortcut_index: int):
        row_id_content = None
        if shortcut_index <= 9:
            row_id_content = ft.Text(str(row_id), color=ft.Colors.PRIMARY, tooltip=f"Shift+{shortcut_index}")
        else:
            row_id_content = ft.Text(str(row_id), color=ft.Colors.PRIMARY)

        deadline_icon = RequestRowHelper._request_deadline_to_icon(
            request_deadline=request_data.request_deadline, request_status=request_data.request_status)
        return ft.DataRow(
            cells=[
                ft.DataCell(deadline_icon if deadline_icon else ft.Text('')),
                ft.DataCell(RequestRowHelper._request_status_to_icon(
                    request_data.request_status)),
                ft.DataCell(row_id_content, on_tap=request_list_form.on_request_edit_open),
                ft.DataCell(ft.Text(str(request_data.request_deadline))),
                ft.DataCell(ft.Text(str(request_data.updated))),
                ft.DataCell(ft.Text(request_data.request_user)),
                ft.DataCell(ft.Text(request_data.iaas_user)),
                ft.DataCell(ft.Text(request_data.request_operation)),
                ft.DataCell(ft.Text(request_data.request_text)),
            ],
            on_select_changed=request_list_form.on_request_row_select,
        )

    @staticmethod
    @Logging.func_logger
    def generate_request_table(
            show_checkbox_column=False,
            heading_row_height=40,
            data_row_max_height=50,
            sort_column_index=2,
            is_sort_ascending=True,
            on_sort_func=None
        ):
        dtRequests = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(
                    ft.Text("依頼ID"), on_sort=on_sort_func
                ),
                ft.DataColumn(
                    ft.Text("リリース希望日"), on_sort=on_sort_func
                ),
                ft.DataColumn(
                    ft.Text("最終更新日"), on_sort=on_sort_func
                ),
                ft.DataColumn(
                    ft.Text("申請者"), on_sort=on_sort_func
                ),
                ft.DataColumn(
                    ft.Text("作業担当者"), on_sort=on_sort_func
                ),
                ft.DataColumn(
                    ft.Text("申請項目"), on_sort=on_sort_func
                ),
                ft.DataColumn(
                    ft.Text("依頼内容"), on_sort=on_sort_func
                ),
            ],
            rows=[],
            show_checkbox_column=show_checkbox_column,
            show_bottom_border=True,
            border=ft.border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST),
            border_radius=10,
            divider_thickness=1,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            heading_row_height=heading_row_height,
            data_row_max_height=data_row_max_height,
            column_spacing=15,
            sort_column_index=sort_column_index,
            sort_ascending=is_sort_ascending,
            # expand=True,
            checkbox_horizontal_margin=15,
            # data_row_color={"hovered": "0x30FF0000"},
        )
        dtRequests.rows = []
        return dtRequests

    @staticmethod
    def _request_deadline_to_icon(request_deadline, request_status):
        now = datetime.datetime.now()
        now_date = datetime.date(now.year, now.month, now.day)
        deadline_datetime = datetime.datetime.strptime(f'{request_deadline} 00:00:00', '%Y/%m/%d %H:%M:%S')
        deadline_date = datetime.date(deadline_datetime.year, deadline_datetime.month, deadline_datetime.day)

        # ステータスが作業完了であれば、Noneを返す
        if request_status == RequestStatus.COMPLETED:
            return None
        if now_date >= deadline_date:
            return ft.Icon(name=ft.Icons.PRIORITY_HIGH_OUTLINED, color=ft.Colors.ERROR, size=18, tooltip='リリース希望日超過')
        else:
            return None

    @staticmethod
    def request_deadline_to_string(request_deadline, request_status, alternative_string):
        now = datetime.datetime.now()
        now_date = datetime.date(now.year, now.month, now.day)
        deadline_datetime = datetime.datetime.strptime(f'{request_deadline} 00:00:00', '%Y/%m/%d %H:%M:%S')
        deadline_date = datetime.date(deadline_datetime.year, deadline_datetime.month, deadline_datetime.day)

        # ステータスが作業完了であれば、Noneを返す
        if request_status == RequestStatus.COMPLETED:
            return ' '
        if now_date >= deadline_date:
            return alternative_string
        else:
            return ' '

    @staticmethod
    def _request_status_to_icon(request_status):
        match request_status:
            case RequestStatus.START:
                return ft.Icon(name=ft.Icons.FIBER_NEW_OUTLINED, color=ft.Colors.PRIMARY, tooltip=RequestStatus.START_FRIENDLY)
            case RequestStatus.APPROVED:
                return ft.Icon(name=ft.Icons.APPROVAL, color=ft.Colors.PRIMARY, tooltip=RequestStatus.APPROVED_FRIENDLY)
            case RequestStatus.APPLYING:
                return ft.ProgressRing(width=16, height=16, stroke_width=2, tooltip=RequestStatus.APPLYING_FRIENDLY)
            case RequestStatus.APPLYING_FAILED:
                return ft.Icon(name=ft.Icons.RUNNING_WITH_ERRORS_OUTLINED, color=ft.Colors.ERROR, tooltip=RequestStatus.APPLYING_FAILED_FRIENDLY)
            case RequestStatus.COMPLETED:
                return ft.Icon(name=ft.Icons.CHECK_CIRCLE, color=ft.Colors.PRIMARY, tooltip=RequestStatus.COMPLETED_FRIENDLY)

    @staticmethod
    @Logging.func_logger
    def delete_selected_requests(request_list_form):
        db_session = db.get_db()
        for row in request_list_form.dtRequests.rows:
            if row.selected:
                request_id = row.cells[RequestRowHelper.REQUEST_ID_COLUMN_NUMBER].content.value
                IaasRequestHelper.delete_request(
                    db_session=db_session,
                    session=request_list_form.session,
                    request_id=request_id,
                )
        db_session.close()
        request_list_form.refresh()
        request_list_form.btnActions.disabled = True
        request_list_form.btnActions.update()

    @staticmethod
    @Logging.func_logger
    def update_request(session):
        db_session = db.get_db()
        IaasRequestHelper.update_request(
            db_session=db_session,
            session=session,
            request_id=session.get('request_id'),
            request_deadline=session.get('request_deadline'),
            request_text=session.get('request_text'),
            job_options=json.dumps(session.get('job_options')),
            request_status=session.get('request_status'),
            iaas_user=session.get('iaas_user'),
        )
        db_session.close()

    @staticmethod
    @Logging.func_logger
    def update_selected_request_status(request_list_form, request_status):
        db_session = db.get_db()
        for row in request_list_form.dtRequests.rows:
            if row.selected:
                request_id = row.cells[RequestRowHelper.REQUEST_ID_COLUMN_NUMBER].content.value
                IaasRequestHelper.update_request_status(
                    db_session=db_session,
                    session=request_list_form.session,
                    request_id=request_id,
                    request_status=request_status,
                )
        db_session.close()
        RequestRowHelper.refresh_data_rows(request_list_form)
        request_list_form.btnActions.disabled = True
        request_list_form.btnActions.update()

    @staticmethod
    @Logging.func_logger
    def update_selected_request_iaas_user(request_list_form, iaas_user):
        db_session = db.get_db()
        for row in request_list_form.dtRequests.rows:
            if row.selected:
                request_id = row.cells[RequestRowHelper.REQUEST_ID_COLUMN_NUMBER].content.value
                IaasRequestHelper.update_request_iaas_user(
                    db_session=db_session,
                    session=request_list_form.session,
                    request_id=request_id,
                    iaas_user=iaas_user,
                )
        db_session.close()
        RequestRowHelper.refresh_data_rows(request_list_form)
        request_list_form.btnActions.disabled = True
        request_list_form.btnActions.update()

    @staticmethod
    @Logging.func_logger
    def refresh_data_rows(request_list_form):
        requests_data = RequestRowHelper.query_request_all(request_list_form)
        request_list_form.dtRequests.rows = []
        shortcut_index = 0
        for request_data in requests_data:
            request_row_data = RequestRowData(
                request_status=request_data.request_status,
                request_deadline=request_data.request_deadline.strftime(
                    '%Y/%m/%d'),
                updated=request_data.updated.strftime('%Y/%m/%d'),
                request_user=request_data.request_user,
                iaas_user=request_data.iaas_user,
                request_operation=request_data.request_operation,
                request_text=request_data.request_text,
            )
            request_list_form.dtRequests.rows.append(
                RequestRowHelper.generate_request_row(
                    request_list_form=request_list_form,
                    row_id=request_data.request_id,
                    request_data=request_row_data,
                    shortcut_index=shortcut_index,
                )
            )
            shortcut_index += 1
        request_list_form.dtRequests.update()
        request_list_form._unregister_key_shortcuts_rows()
        request_list_form._register_key_shortcuts_rows()

    @staticmethod
    @Logging.func_logger
    def refresh_page_indicator(request_list_form):
        range_min, range_max, request_data_count = RequestRowHelper.get_page_range(
            request_list_form)
        request_list_form.textRequestsRange.value = "{}-{} / {}".format(
            range_min, range_max, request_data_count)
        request_list_form.textRequestsRange.update()

        if (request_list_form.data_row_offset + 1 + request_list_form.DATA_ROW_MAX) >= request_data_count:
            request_list_form.btnNextPage.disabled = True
            request_list_form.btnNextPage.icon_color = ft.Colors.ON_INVERSE_SURFACE
        else:
            request_list_form.btnNextPage.disabled = False
            request_list_form.btnNextPage.icon_color = ft.Colors.ON_SURFACE_VARIANT
        request_list_form.btnNextPage.update()

        if (request_list_form.data_row_offset + 1 - request_list_form.DATA_ROW_MAX) < 0:
            request_list_form.btnPreviousPage.disabled = True
            request_list_form.btnPreviousPage.icon_color = ft.Colors.ON_INVERSE_SURFACE
        else:
            request_list_form.btnPreviousPage.disabled = False
            request_list_form.btnPreviousPage.icon_color = ft.Colors.ON_SURFACE_VARIANT
        request_list_form.btnPreviousPage.update()

    @staticmethod
    @Logging.func_logger
    def get_page_range(request_list_form):
        record_count = RequestRowHelper.count_request_all(request_list_form)
        range_min = 0 if record_count == 0 else (
            request_list_form.data_row_offset + 1)
        if (request_list_form.data_row_offset + request_list_form.DATA_ROW_MAX) <= record_count:
            range_max = request_list_form.data_row_offset + request_list_form.DATA_ROW_MAX
        else:
            range_max = record_count
        return range_min, range_max, record_count

    @staticmethod
    @Logging.func_logger
    def query_request_all(request_list_form):
        db_session = db.get_db()
        order_spec = None
        filters = request_list_form.get_query_filters()
        match request_list_form.session.get('sort_target_column'):
            case '依頼ID':
                order_spec = IaasRequestHelper.get_order_spec_request_id(
                    request_list_form.dtRequests.sort_ascending)
            case 'リリース希望日':
                order_spec = IaasRequestHelper.get_order_spec_request_deadline(
                    request_list_form.dtRequests.sort_ascending)
            case '最終更新日':
                order_spec = IaasRequestHelper.get_order_spec_updated(
                    request_list_form.dtRequests.sort_ascending)
            case '申請者':
                order_spec = IaasRequestHelper.get_order_spec_request_user(
                    request_list_form.dtRequests.sort_ascending)
            case '作業担当者':
                order_spec = IaasRequestHelper.get_order_spec_iaas_user(
                    request_list_form.dtRequests.sort_ascending)
            case '申請項目':
                order_spec = IaasRequestHelper.get_order_spec_request_operation(
                    request_list_form.dtRequests.sort_ascending)
            case '依頼内容':
                order_spec = IaasRequestHelper.get_order_spec_request_text(
                    request_list_form.dtRequests.sort_ascending)

        requests_data = IaasRequestHelper.get_requests(
            db_session=db_session,
            filters=filters,
            order_spec=order_spec,
            offset_row=request_list_form.data_row_offset,
            limit_rows=request_list_form.DATA_ROW_MAX
        )
        db_session.close()
        return requests_data

    @staticmethod
    @Logging.func_logger
    def count_request_all(request_list_form):
        db_session = db.get_db()
        filters = request_list_form.get_query_filters()
        requests_data = IaasRequestHelper.count_requests(db_session, filters)
        db_session.close()
        return requests_data

    @staticmethod
    @Logging.func_logger
    def count_request(filters):
        db_session = db.get_db()
        requests_data = IaasRequestHelper.count_requests(db_session, filters)
        db_session.close()
        return requests_data

    @staticmethod
    @Logging.func_logger
    def sort_column(request_list_form, session, column_label):
        session.set('sort_target_column', column_label)
        # ソート対象が同じ列の場合、昇順と降順を逆転させる
        if session.get('sort_target_column') == session.get('sort_target_column_old') \
                or not session.get('sort_target_column_old'):
            request_list_form.dtRequests.sort_ascending = not request_list_form.dtRequests.sort_ascending

        match column_label:
            case '依頼ID':
                request_list_form.dtRequests.sort_column_index = 2
            case 'リリース希望日':
                request_list_form.dtRequests.sort_column_index = 3
            case '最終更新日':
                request_list_form.dtRequests.sort_column_index = 4
            case '申請者':
                request_list_form.dtRequests.sort_column_index = 5
            case '作業担当者':
                request_list_form.dtRequests.sort_column_index = 6
            case '申請項目':
                request_list_form.dtRequests.sort_column_index = 7
            case '依頼内容':
                request_list_form.dtRequests.sort_column_index = 8
        session.set('sort_target_column_old', column_label)
        RequestRowHelper.refresh_data_rows(request_list_form)
