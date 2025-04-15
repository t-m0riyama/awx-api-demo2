import os

import flet as ft

from awx_demo.components.compounds.requests_indicator import RequestsIndicator
from awx_demo.components.forms.context_help_form import ContextHelpForm
from awx_demo.components.forms.helper.request_row_helper import RequestRowData, RequestRowHelper
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.components.wizards.edit_request_wizard import EditRequestWizard
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class InProgressTabForm(ft.Card):

    # const
    CONTENT_HEIGHT = 640
    CONTENT_WIDTH = 1000
    BODY_HEIGHT = 590
    REQUEST_LIST_MAX_HEIGHT = 600
    FILTERED_IAAS_USERS_DEFAULT = "root,admin,awxcli"
    REQUEST_ID_COLUMN_NUMBER = 2
    DESCRIPTION_FONT_SIZE = 12
    PANEL_PADDING_SIZE = 5
    DATA_ROW_MAX = 10
    DEFAULT_SORT_TARGET_COLUMN = 'リリース希望日'
    DEFAULT_SORT_COLUMN_INDEX = 3
    DEFAULT_SORT_ASCENDING = True
    DAYS_AFTER_DEADLINE_DEFAULT = 3
    DAYS_BEFORE_COMPLETED_TARGET_DEFAULT = 30

    def __init__(
        self,
        session,
        page,
        height=CONTENT_HEIGHT,
        width=CONTENT_WIDTH,
        body_height=BODY_HEIGHT,
    ):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.data_row_offset = 0
        self.session.set("sort_target_column", self.DEFAULT_SORT_TARGET_COLUMN)
        self.days_after_deadline = int(os.getenv("RMX_DAYS_AFTER_DEADLINE", self.DAYS_AFTER_DEADLINE_DEFAULT))
        self.days_before_completed_target = int(os.getenv("RMX_DAYS_BEFORE_COMPLETED_TARGET", self.DAYS_BEFORE_COMPLETED_TARGET_DEFAULT))
        content_md = f"""
ダッシュボードは、現在対応中の申請件数とその一覧を示します。
***

### :small_blue_diamond: 自身の申請: 自身が担当する申請件数です。
* 申請中: 状態が「申請中」の申請件数を示します。
* 承認済み: 状態が「承認済み」の申請件数を示します。
* 作業完了: 状態が「申請中」の申請件数を示します。直近{self.days_before_completed_target}日間の申請が対象です。

### :small_blue_diamond: 全ての申請: 全体の申請件数です。
* 未割り当て: 作業担当者を割り当てていない申請件数を示します。
* リリース希望日: 変作業担当者を割り当てていない申請件数を示します。リリース希望日が{self.days_after_deadline}日以内に迫った申請を対象です。
* 作業中（失敗）: 作業の実行中に失敗した申請件数を示します。

### :small_blue_diamond: 申請一覧: 申請件数タイルの選択に応じた一覧を示します。
        """

        formContextHelp = ContextHelpForm(self.session, self.page, title=f"ダッシュボードについて", content_md=content_md)
        self.dlgContextForm = ft.AlertDialog(
            modal=True,
            content=formContextHelp,
            actions=[
                ft.FilledButton("OK", tooltip="OK", on_click=self.on_click_context_help_ok),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # controls
        self.btnHelp = ft.IconButton(
            icon=ft.Icons.HELP_OUTLINE_ROUNDED,
            icon_color=ft.Colors.ON_SURFACE_VARIANT,
            tooltip="ヘルプ",
            on_click=self.on_click_context_help,
        )
        self.btnReload = ft.IconButton(
            icon=ft.Icons.SYNC,
            icon_color=ft.Colors.ON_SURFACE_VARIANT,
            tooltip="再読み込み (Control+Alt+R)",
            on_click=lambda e: self.refresh(),
            # autofocus=True,
        )

        requests_count = self.count_requests()
        self.panelListMine = ft.ExpansionPanelList(
            expand_icon_color=ft.Colors.SECONDARY,
            divider_color=ft.Colors.SECONDARY,
            expanded_header_padding=ft.padding.symmetric(vertical=0),
            controls=[],
        )
        panelMine = ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text("自身の申請")),
            expanded=True,
        )
        self.indicatorStart = RequestsIndicator(
            title=RequestStatus.START_FRIENDLY,
            indicator_text=requests_count['requests_count_start'],
            icon=ft.Icon(ft.Icons.FIBER_NEW, size=RequestsIndicator.ICON_SIZE),
            indicator_text_font_size=RequestsIndicator.REQUESTS_COUNT_FONT_SIZE_MEDIUM,
            on_click=self.on_click_request_indicator,
            tooltip="申請中の申請件数",
            border_color=ft.Colors.PRIMARY,
        )
        self.indicatorApproved = RequestsIndicator(
            title=RequestStatus.APPROVED_FRIENDLY,
            indicator_text=requests_count['requests_count_approved'],
            icon=ft.Icon(ft.Icons.APPROVAL, size=RequestsIndicator.ICON_SIZE),
            indicator_text_font_size=RequestsIndicator.REQUESTS_COUNT_FONT_SIZE_MEDIUM,
            on_click=self.on_click_request_indicator,
            tooltip="承認済みの申請件数",
        )
        self.indicatorCompleted = RequestsIndicator(
            title=RequestStatus.COMPLETED_FRIENDLY,
            indicator_text=requests_count['requests_count_completed'],
            icon=ft.Icon(ft.Icons.CHECK_CIRCLE, size=RequestsIndicator.ICON_SIZE),
            indicator_text_font_size=RequestsIndicator.REQUESTS_COUNT_FONT_SIZE_MEDIUM,
            on_click=self.on_click_request_indicator,
            tooltip="完了済みの申請件数",
        )
        panelMine.content = ft.Container(
            content=ft.Row(
                controls=[
                    self.indicatorStart,
                    self.indicatorApproved,
                    self.indicatorCompleted,
                ],
                expand=True,
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
                # tight=True,
            ),
            padding=ft.padding.all(self.PANEL_PADDING_SIZE),
        )
        self.panelListMine.controls.append(panelMine)

        self.panelListAll = ft.ExpansionPanelList(
            expand_icon_color=ft.Colors.SECONDARY,
            divider_color=ft.Colors.SECONDARY,
            expanded_header_padding=ft.padding.symmetric(vertical=0),
            controls=[],
        )
        panelAll = ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text("全ての申請")),
            expanded=True,
        )
        self.indicatorUnassigned = RequestsIndicator(
            title="未割り当て",
            indicator_text=requests_count['requests_count_unassigned'],
            icon=ft.Icon(ft.Icons.ASSIGNMENT_IND_OUTLINED, size=RequestsIndicator.ICON_SIZE, color=ft.Colors.YELLOW_800,),
            indicator_text_font_size=RequestsIndicator.REQUESTS_COUNT_FONT_SIZE_MEDIUM,
            on_click=self.on_click_request_indicator,
            tooltip="作業担当者が未割り当ての申請件数",
        )
        self.indicatorDeadline = RequestsIndicator(
            title="リリース希望日",
            indicator_text=requests_count['requests_count_deadline'],
            icon=ft.Icon(ft.Icons.WARNING_AMBER, size=RequestsIndicator.ICON_SIZE, color=ft.Colors.YELLOW_800),
            indicator_text_font_size=RequestsIndicator.REQUESTS_COUNT_FONT_SIZE_MEDIUM,
            title_font_size=RequestsIndicator.TITLE_FONT_SIZE_SMALL,
            on_click=self.on_click_request_indicator,
            tooltip=f"リリース希望日が{self.days_after_deadline}日以内に迫った申請件数",
        )
        self.indicatorApplyFailed = RequestsIndicator(
            title=RequestStatus.APPLYING_FAILED_FRIENDLY,
            indicator_text=requests_count['requests_count_applying_failed'],
            icon=ft.Icon( ft.Icons.RUNNING_WITH_ERRORS_OUTLINED, size=RequestsIndicator.ICON_SIZE, color=ft.Colors.ERROR),
            indicator_text_font_size=RequestsIndicator.REQUESTS_COUNT_FONT_SIZE_MEDIUM,
            on_click=self.on_click_request_indicator,
            tooltip=f"実行中に失敗した申請件数",
        )
        panelAll.content = ft.Container(
            content=ft.Row(
                controls=[
                    self.indicatorUnassigned,
                    self.indicatorDeadline,
                    self.indicatorApplyFailed,
                ],
                expand=True,
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
                # tight=True,
            ),
            padding=ft.padding.all(self.PANEL_PADDING_SIZE),
        )
        self.panelListAll.controls.append(panelAll)

        self.panelListDeadline = ft.ExpansionPanelList(
            expand_icon_color=ft.Colors.SECONDARY,
            divider_color=ft.Colors.SECONDARY,
            expanded_header_padding=ft.padding.symmetric(vertical=0),
            controls=[],
        )
        panelRequestList = ft.ExpansionPanel(
            header=ft.ListTile(title=ft.Text("リリース希望日の近い申請")),
            expanded=True,
        )

        self.dtRequests = RequestRowHelper.generate_request_table(
            show_checkbox_column=False,
            heading_row_height=25,
            data_row_max_height=50,
            sort_column_index=self.DEFAULT_SORT_COLUMN_INDEX,
            is_sort_ascending=self.DEFAULT_SORT_ASCENDING,
            on_sort_func=self.on_click_heading_column,
        )
        self.rowRequests = self.generate_data_rows()

        panelRequestList.content = ft.Container(
            content=ft.Row(
                controls=[
                    self.dtRequests,
                ],
                # expand=True,
                height=self.REQUEST_LIST_MAX_HEIGHT,
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
                # tight=True,
            ),
            padding=ft.padding.all(self.PANEL_PADDING_SIZE),
        )
        self.panelListDeadline.controls.append(panelRequestList)

        # Content
        body = ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"sm": 12},
                            controls=[
                                ft.Row(
                                    controls=[
                                        self.btnHelp,
                                        self.btnReload,
                                    ],
                                    alignment=ft.MainAxisAlignment.END,
                                    spacing=0,
                                )
                            ],
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"sm": 6},
                            controls=[
                                self.panelListMine,
                            ],
                        ),
                        ft.Column(
                            col={"sm": 6},
                            controls=[
                                self.panelListAll,
                            ],
                        ),
                    ],
                ),
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"sm": 12},
                            controls=[
                                ft.SelectionArea(content=self.panelListDeadline),
                            ]
                        ),
                    ],
                ),
            ],
            height=self.body_height,
            alignment=ft.MainAxisAlignment.START,
            # auto_scroll=True,
            scroll=True,
        )

        self.controls = ft.Container(
            ft.Column(
                [
                    body,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            # width=self.content_width,
            height=self.content_height,
            padding=ft.Padding(top=10, bottom=0, left=10, right=10),
        )
        super().__init__(content=self.controls, expand=True)

    def count_requests(self):
        requests_count_start = RequestRowHelper.count_request(
            filters=self.get_query_filters_by_status(status=[RequestStatus.START])
        )
        requests_count_approved = RequestRowHelper.count_request(
            filters=self.get_query_filters_by_status(status=[RequestStatus.APPROVED])
        )
        requests_count_completed = RequestRowHelper.count_request(
            filters=self.get_query_filters_by_status(
                status=[RequestStatus.COMPLETED],
                days_before_target=self.days_before_completed_target
            )
        )
        requests_count_unassigned = RequestRowHelper.count_request(
            filters=self.get_query_filters_unassigned()
        )
        requests_count_deadline = RequestRowHelper.count_request(
            filters=self.get_query_filters_deadline(days_after_deadline=self.days_after_deadline)
        )
        requests_count_applying_failed = RequestRowHelper.count_request(
            filters=self.get_query_filters_by_status(status=[RequestStatus.APPLYING_FAILED])
        )

        return {
            "requests_count_start": requests_count_start,
            "requests_count_approved": requests_count_approved,
            "requests_count_completed": requests_count_completed,
            "requests_count_unassigned": requests_count_unassigned,
            "requests_count_deadline": requests_count_deadline,
            "requests_count_applying_failed": requests_count_applying_failed,
        }

    def generate_data_rows(self):
        requests_data = RequestRowHelper.query_request_all(self)
        shortcut_index = 0
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
                    request_list_form=self,
                    row_id=request_data.request_id,
                    request_data=request_row_data,
                    shortcut_index=shortcut_index,
                )
            )
            shortcut_index += 1
        rowRequests = ft.ResponsiveRow(
            [
                ft.SelectionArea(
                    content=ft.Column(
                        col={"sm": 12},
                        controls=[self.dtRequests],
                        scroll=ft.ScrollMode.AUTO,
                    )
                )
            ],
            expand=1,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )
        return rowRequests

    @Logging.func_logger
    def on_change_iaas_user(self, e):
        self.session.set("iaas_user", e.control.value)

    @Logging.func_logger
    def get_query_filters(self):
        filters = []
        filters.append(IaasRequestHelper.get_filter_request_text(
            self.session.get('request_text_search_string')))
        filters.append(IaasRequestHelper.get_filter_request_status(
            [RequestStatus.APPROVED, RequestStatus.APPLYING, RequestStatus.APPLYING_FAILED, RequestStatus.START]))
        if self.session.get('user_role') == UserRole.USER_ROLE:
            filters.append(IaasRequestHelper.get_filter_request_user(
                self.session.get('awx_loginid')))
        return filters

    @Logging.func_logger
    def get_query_filters_by_status(self, status=None, days_before_target=0):
        filters = []
        filters.append(IaasRequestHelper.get_filter_request_text(
            self.session.get('request_text_search_string')))
        if self.session.get('user_role') == UserRole.USER_ROLE:
            filters.append(IaasRequestHelper.get_filter_request_user(
                self.session.get('awx_loginid')))
        if days_before_target > 0:
            filters.append(IaasRequestHelper.get_filter_request_updated(days_before_target))
        filters.append(IaasRequestHelper.get_filter_request_status(status))
        return filters

    @Logging.func_logger
    def get_query_filters_unassigned(self):
        filters = []
        filters.append(IaasRequestHelper.get_filter_request_text(
            self.session.get('request_text_search_string')))
        if self.session.get('user_role') == UserRole.USER_ROLE:
            filters.append(IaasRequestHelper.get_filter_request_user(
                self.session.get('awx_loginid')))
        filters.append(IaasRequestHelper.get_filter_iaas_user_is_null())
        return filters

    @Logging.func_logger
    def get_query_filters_deadline(self, days_after_deadline=0):
        filters = []
        filters.append(IaasRequestHelper.get_filter_request_text(
            self.session.get('request_text_search_string')))
        if self.session.get('user_role') == UserRole.USER_ROLE:
            filters.append(IaasRequestHelper.get_filter_request_user(
                self.session.get('awx_loginid')))
        filters.append(IaasRequestHelper.get_filter_request_status(
            [RequestStatus.APPROVED, RequestStatus.APPLYING, RequestStatus.APPLYING_FAILED, RequestStatus.START]))
        filters.append(IaasRequestHelper.get_filter_request_deadline(days_after_deadline))
        return filters

    @Logging.func_logger
    def refresh(self):
        requests_count = self.count_requests()
        self.indicatorStart.set_indicator_text(requests_count['requests_count_start'])
        self.indicatorApproved.set_indicator_text(requests_count['requests_count_approved'])
        self.indicatorCompleted.set_indicator_text(requests_count['requests_count_completed'])
        self.indicatorUnassigned.set_indicator_text(requests_count['requests_count_unassigned'])
        self.indicatorDeadline.set_indicator_text(requests_count['requests_count_deadline'])
        self.indicatorApplyFailed.set_indicator_text(requests_count['requests_count_applying_failed'])
        RequestRowHelper.refresh_data_rows(self)
        self.panelListMine.update()
        self.panelListAll.update()
        self.panelListDeadline.update()

    @Logging.func_logger
    def on_click_heading_column(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self._unlock_form_controls()
        RequestRowHelper.sort_column(self, self.session, e.control.label.value)

    @Logging.func_logger
    def on_click_request_indicator(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self._unlock_form_controls()
        self.indicatorStart.set_border()
        self.indicatorApproved.set_border()
        self.indicatorCompleted.set_border()
        self.indicatorUnassigned.set_border()
        self.indicatorDeadline.set_border()
        self.indicatorApplyFailed.set_border()
        e.control.set_border(color=ft.Colors.PRIMARY)
        self.panelListMine.update()
        self.panelListAll.update()

    @Logging.func_logger
    def on_request_row_select(self, e=None, selected_index=None):
        self._lock_form_controls()
        # キーボードショートカットから呼ばれた場合、
        # selected_indexにセットされている値を申請一覧のインデックスの代わりに利用する
        if selected_index is not None:
            self.dtRequests.rows[selected_index].selected = not self.dtRequests.rows[selected_index].selected
            self.dtRequests.rows[selected_index].update()
        else:
            e.control.selected = not e.control.selected
            e.control.update()
        self.activate_action_button()
        self._unlock_form_controls()

    @Logging.func_logger
    def on_request_edit_open(self, e=None, request_id=None):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return

        # キーボードショートカットから呼ばれた場合、
        # request_idにセットされている値を申請IDの代わりに利用する
        request_id = request_id if request_id is not None else e.control.content.value
        self.session.set("request_id", request_id)
        self._unlock_form_controls()
        self.open_edit_request_dialog()

    @Logging.func_logger
    def open_edit_request_dialog(self):
        wzdEditRequest = EditRequestWizard(
            session=self.session,
            page=self.page,
            parent_refresh_func=self.refresh,
        )
        wzdEditRequest.open_wizard()

    @Logging.func_logger
    def on_click_context_help(self, e):
        self._lock_form_controls()
        self._save_keyboard_shortcuts()
        self.page.open(self.dlgContextForm)
        self.dlgContextForm.open = True
        self._unlock_form_controls()
        self.page.update()

    @Logging.func_logger
    def on_click_context_help_ok(self, e):
        self.page.close(self.dlgContextForm)
        self.dlgContextForm.open = False
        self._restore_key_shortcuts()
        self.page.update()

    @Logging.func_logger
    def _lock_form_controls(self):
        # クリック連打対策
        self.controls.disabled = True
        self.controls.update()

    @Logging.func_logger
    def _unlock_form_controls(self):
        # クリック連打対策解除
        self.controls.disabled = False
        self.controls.update()

    @Logging.func_logger
    def _save_keyboard_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        keyboard_shortcut_manager.save_key_shortcuts()
        keyboard_shortcut_manager.clear_key_shortcuts()

    @Logging.func_logger
    def _restore_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        keyboard_shortcut_manager.restore_key_shortcuts()

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=lambda e: self.tfSearchRequestText.focus(),
        )
        # 申請一覧の再読み込み
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="R", shift=False, ctrl=True, alt=True, meta=False,
            ),
            func=lambda e: self.refresh(),
        )
        self._register_key_shortcuts_rows()

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        if self.page:
            keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
            # autofocus=Trueである、最初のコントロールにフォーカスを移動する
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="F", shift=True, ctrl=False, alt=True, meta=False
                ),
            )
            # 申請一覧の再読み込み
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key="R", shift=False, ctrl=True, alt=True, meta=False,
                ),
            )
            self._unregister_key_shortcuts_rows()

    @Logging.func_logger
    def _register_key_shortcuts_rows(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        max_row_shortcuts = min(10, len(self.dtRequests.rows))
        # 申請の編集
        for row_index in range(0, max_row_shortcuts):
            request_id = self.dtRequests.rows[row_index].cells[self.REQUEST_ID_COLUMN_NUMBER].content.value
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key=f"{row_index}", shift=True, ctrl=False, alt=False, meta=False,
                ),
                func=lambda e, request_id=request_id: self.on_request_edit_open(request_id=request_id),
            )

    @Logging.func_logger
    def _unregister_key_shortcuts_rows(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # 申請の編集
        for row_index in range(0, 10):
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key=str(row_index), shift=True, ctrl=False, alt=False, meta=False,
                ),
            )
