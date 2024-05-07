import abc

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.forms.delete_confirm_form import DeleteConfirmForm
from awx_demo.components.forms.helper.request_row_helper import RequestRowData, RequestRowHelper
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.components.wizards.edit_request_wizard import EditRequestWizard
from awx_demo.components.wizards.new_request_wizard import NewRequestWizard
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class BaseRequestListForm(ft.UserControl, metaclass=abc.ABCMeta):

    # const
    CONTENT_HEIGHT = 640
    CONTENT_WIDTH = 1000
    BODY_HEIGHT = 540
    DATA_ROW_MAX = 20
    DEFAULT_SORT_TARGET_COLUMN = "最終更新日"
    DEFAULT_SORT_COLUMN_INDEX = 3
    DEFAULT_SORT_ASCENDING = True
    FORM_TITLE = "最新の申請"

    def __init__(self, session, page: ft.Page):
        self.session = session
        self.page = page
        self.data_row_offset = 0
        self.session.set("sort_target_column", self.DEFAULT_SORT_TARGET_COLUMN)
        super().__init__()

    @abc.abstractmethod
    def get_query_filters(self):
        pass

    def activate_action_button(self):
        # １件以上の申請が選択されていて、申請者以外のロールである場合、アクションメニューを有効化
        self.btnActions.disabled = True
        if self.session.get("user_role") != UserRole.USER_ROLE:
            for row in self.dtRequests.rows:
                if row.selected:
                    self.btnActions.disabled = False
                    break
        self.btnActions.update()

    def open_delete_confirm_dialog(self):
        formDeleteConfirm = DeleteConfirmForm(self.session, self.page)
        self.dlgDeleteConfirm = ft.AlertDialog(
            modal=True,
            # title=ft.Text("削除の確認"),
            content=formDeleteConfirm,
            actions=[
                ft.ElevatedButton("はい", on_click=self.on_click_delete_request_yes),
                ft.FilledButton(
                    "キャンセル", on_click=self.on_click_delete_request_cancel
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.dialog = self.dlgDeleteConfirm
        self.dlgDeleteConfirm.open = True
        self.page.update()

    def open_add_request_dialog(self):
        SessionHelper.clean_request_from_session(self.session)
        wzdNewRequest = NewRequestWizard(self.session, self.page, self.refresh)
        wzdNewRequest.open_wizard()

    def open_edit_request_dialog(self):
        wzdEditRequest = EditRequestWizard(
            session=self.session,
            page=self.page,
            parent_refresh_func=self.refresh,
        )
        wzdEditRequest.open_wizard()

    def refresh(self):
        RequestRowHelper.refresh_data_rows(self)
        RequestRowHelper.refresh_page_indicator(self)

    def build(self):
        formTitle = FormTitle(self.FORM_TITLE, None, self.CONTENT_WIDTH)
        self.dtRequests = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("")),
                ft.DataColumn(
                    ft.Text("依頼ID"), on_sort=self.on_click_heading_column
                ),
                ft.DataColumn(
                    ft.Text("リリース希望日"), on_sort=self.on_click_heading_column
                ),
                ft.DataColumn(
                    ft.Text("最終更新日"), on_sort=self.on_click_heading_column
                ),
                ft.DataColumn(
                    ft.Text("申請者"), on_sort=self.on_click_heading_column
                ),
                ft.DataColumn(
                    ft.Text("作業担当者"), on_sort=self.on_click_heading_column
                ),
                ft.DataColumn(
                    ft.Text("申請項目"), on_sort=self.on_click_heading_column
                ),
                ft.DataColumn(
                    ft.Text("依頼内容"), on_sort=self.on_click_heading_column
                ),
            ],
            rows=[],
            show_checkbox_column=True,
            show_bottom_border=True,
            border=ft.border.all(2, ft.colors.SURFACE_VARIANT),
            border_radius=10,
            divider_thickness=1,
            heading_row_color=ft.colors.SURFACE_VARIANT,
            heading_row_height=40,
            data_row_max_height=60,
            column_spacing=15,
            sort_column_index=self.DEFAULT_SORT_COLUMN_INDEX,
            sort_ascending=self.DEFAULT_SORT_ASCENDING,
            # expand=True,
            checkbox_horizontal_margin=15,
            # data_row_color={"hovered": "0x30FF0000"},
        )

        requests_data = RequestRowHelper.query_request_all(self)
        self.dtRequests.rows = []
        for request_data in requests_data:
            request_row_data = RequestRowData(
                request_status=request_data.request_status,
                request_deadline=request_data.request_deadline.strftime("%Y/%m/%d"),
                updated=request_data.updated.strftime("%Y/%m/%d"),
                request_user=request_data.request_user,
                iaas_user=request_data.iaas_user,
                request_operation=request_data.request_operation,
                request_text=request_data.request_text,
            )
            self.dtRequests.rows.append(
                RequestRowHelper.generate_request_row(
                    self,
                    request_data.request_id,
                    request_row_data,
                )
            )
        self.rowRequests = ft.ResponsiveRow(
            [
                ft.Column(
                    col={"sm": 12},
                    controls=[self.dtRequests],
                    scroll=True,
                )
            ],
            expand=1,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        self.btnAddRequest = ft.FilledButton(
            text="新規作成",
            icon=ft.icons.ADD,
            on_click=self.on_click_add_request,
        )

        iaas_users = AWXApiHelper.get_users(
            self.session.get("awx_url"),
            self.session.get("awx_loginid"),
            self.session.get("awx_password"),
        )
        # iaas_users = []  # for DEBUG
        iaas_user_items = []
        for iaas_user in iaas_users:
            iaas_user_items.append(
                ft.PopupMenuItem(
                    icon=ft.icons.ACCOUNT_CIRCLE_OUTLINED,
                    text=iaas_user["username"],
                    on_click=self.on_change_request_iaas_user,
                )
            )

        popup_menu_items = []
        match self.session.get("user_role"):
            case UserRole.ADMIN_ROLE:
                popup_menu_items = [
                    ft.PopupMenuItem(icon=ft.icons.ROCKET_LAUNCH, text="実行"),
                    ft.PopupMenuItem(
                        content=ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(
                                    icon=ft.icons.FIBER_NEW,
                                    text=RequestStatus.START_FRIENDLY,
                                    on_click=self.on_change_request_status,
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.icons.APPROVAL,
                                    text=RequestStatus.APPROVED_FRIENDLY,
                                    on_click=self.on_change_request_status,
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.icons.CHECK_CIRCLE,
                                    text=RequestStatus.COMPLETED_FRIENDLY,
                                    on_click=self.on_change_request_status,
                                ),
                            ],
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.MULTIPLE_STOP),
                                    ft.Text("状態の変更"),
                                ],
                            ),
                        ),
                    ),
                    ft.PopupMenuItem(
                        content=ft.PopupMenuButton(
                            items=iaas_user_items,
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.ASSIGNMENT_IND_OUTLINED),
                                    ft.Text("作業担当者の変更"),
                                ],
                            ),
                        ),
                    ),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(
                        icon=ft.icons.DELETE,
                        text="削除",
                        on_click=self.on_selected_delete,
                    ),
                ]

            case UserRole.OPERATOR_ROLE:
                popup_menu_items = [
                    ft.PopupMenuItem(icon=ft.icons.ROCKET_LAUNCH, text="実行"),
                    ft.PopupMenuItem(
                        content=ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(
                                    icon=ft.icons.CHECK_CIRCLE,
                                    text=RequestStatus.COMPLETED_FRIENDLY,
                                    on_click=self.on_change_request_status,
                                ),
                            ],
                            content=ft.Row(
                                [
                                    ft.Icon(ft.icons.MULTIPLE_STOP),
                                    ft.Text("状態の変更"),
                                ],
                            ),
                        ),
                    ),
                ]
            case UserRole.USER_ROLE:
                pass

        self.btnActions = ft.PopupMenuButton(
            items=popup_menu_items,
            icon=ft.icons.ARROW_DROP_DOWN_CIRCLE_OUTLINED,
            tooltip="その他のアクション",
            disabled=True,
        )
        self.tfSearchRequestText = ParameterInputText(
            label="依頼内容に含まれる文字を検索",
            width=340,
            on_submit=self.on_click_search_request_text,
        )
        self.btnSearchRequestText = ft.IconButton(
            icon=ft.icons.SEARCH,
            icon_color=ft.colors.ON_SURFACE_VARIANT,
            on_click=self.on_click_search_request_text,
            tooltip="検索",
        )
        range_min, range_max, request_data_count = RequestRowHelper.get_page_range(self)
        self.textRequestsRange = ft.Text(
            "{}-{} / {}".format(range_min, range_max, request_data_count)
        )
        self.btnPreviousPage = ft.IconButton(
            icon=ft.icons.ARROW_LEFT,
            icon_color=ft.colors.ON_INVERSE_SURFACE,
            on_click=self.on_click_previous_page,
            disabled=True,
        )
        self.btnNextPage = ft.IconButton(
            icon=ft.icons.ARROW_RIGHT,
            icon_color=ft.colors.ON_SURFACE_VARIANT,
            on_click=self.on_click_next_page,
        )

        # Content
        header = ft.Container(
            formTitle,
        )
        body = ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        ft.Row(
                            col={"sm": 3, "md": 3, "lg": 3, "xl": 3, "xxl": 3},
                            controls=[
                                self.btnAddRequest,
                                self.btnActions,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Row(
                            col={"sm": 6, "md": 6, "lg": 6, "xl": 7, "xxl": 7},
                            controls=[
                                self.tfSearchRequestText,
                                self.btnSearchRequestText,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            col={"sm": 3, "md": 3, "lg": 3, "xl": 2, "xxl": 2},
                            controls=[
                                self.btnPreviousPage,
                                self.textRequestsRange,
                                self.btnNextPage,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.rowRequests,
            ],
            height=self.BODY_HEIGHT,
        )

        return ft.Container(
            ft.ResponsiveRow(
                [
                    ft.Column(
                        col={"sm": 12},
                        controls=[
                            header,
                            body,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ]
            ),
            # width=self.CONTENT_WIDTH,
            height=self.CONTENT_HEIGHT,
            # padding=ft.padding.all(0),
        )

    def on_request_row_select(self, e):
        e.control.selected = not e.control.selected
        self.activate_action_button()
        e.control.update()

    def on_request_edit_open(self, e):
        self.session.set("request_id", e.control.content.value)
        self.open_edit_request_dialog()

    def on_change_request_status(self, e):
        match e.control.text:
            case RequestStatus.START_FRIENDLY:
                request_status = RequestStatus.START
            case RequestStatus.APPROVED_FRIENDLY:
                request_status = RequestStatus.APPROVED
            case RequestStatus.COMPLETED_FRIENDLY:
                request_status = RequestStatus.COMPLETED
            case _:
                request_status = ""
        RequestRowHelper.update_selected_request_status(self, request_status)

    def on_change_request_iaas_user(self, e):
        RequestRowHelper.update_selected_request_iaas_user(self, e.control.text)

    def on_click_heading_column(self, e):
        RequestRowHelper.sort_column(self, self.session, e.control.label.value)

    def on_selected_delete(self, e):
        self.open_delete_confirm_dialog()

    def on_click_add_request(self, e):
        self.open_add_request_dialog()

    def on_click_delete_request_cancel(self, e):
        self.dlgDeleteConfirm.open = False
        self.page.update()

    def on_click_delete_request_yes(self, e):
        RequestRowHelper.delete_selected_requests(self)
        self.dlgDeleteConfirm.open = False
        self.page.update()
        self.refresh()

    def on_click_edit_request_cancel(self, e):
        self.dlgEditRequest.open = False
        self.page.update()

    def on_click_edit_request_execute(self, e):
        Logging.info(self.session.get("job_options"))
        self.dlgEditRequest.open = False
        self.page.update()

    def on_click_edit_request_save(self, e):
        RequestRowHelper.update_request(self.session)
        self.dlgEditRequest.open = False
        self.page.update()
        self.refresh()

    def on_click_next_page(self, e):
        request_data_count = RequestRowHelper.count_request_all(self)
        if (self.data_row_offset + 1) < request_data_count:
            self.data_row_offset += self.DATA_ROW_MAX
            self.refresh()

    def on_click_previous_page(self, e):
        if (self.data_row_offset + 1) > self.DATA_ROW_MAX:
            self.data_row_offset -= self.DATA_ROW_MAX
            self.refresh()

    def on_click_search_request_text(self, e):
        self.data_row_offset = 0
        self.session.set("request_text_search_string", self.tfSearchRequestText.value)
        self.refresh()
