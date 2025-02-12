import abc
import os

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.forms.delete_confirm_form import DeleteConfirmForm
from awx_demo.components.forms.helper.request_row_helper import RequestRowData, RequestRowHelper
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.components.wizards.edit_request_wizard import EditRequestWizard
from awx_demo.components.wizards.new_request_wizard import NewRequestWizard
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class BaseRequestListForm(ft.Card, metaclass=abc.ABCMeta):

    # const
    CONTENT_HEIGHT = 640
    CONTENT_WIDTH = 1000
    BODY_HEIGHT = 540
    DATA_ROW_MAX = 20
    DEFAULT_SORT_TARGET_COLUMN = "最終更新日"
    DEFAULT_SORT_COLUMN_INDEX = 3
    DEFAULT_SORT_ASCENDING = True
    FORM_TITLE = "最新の申請"
    FILTERED_IAAS_USERS_DEFAULT = "root,admin,awxcli"
    REQUEST_ID_COLUMN_NUMBER = 1

    def __init__(self, session, page: ft.Page):
        self.session = session
        self.page = page
        self.data_row_offset = 0
        self.session.set("sort_target_column", self.DEFAULT_SORT_TARGET_COLUMN)

        formTitle = FormTitle(self.FORM_TITLE, None)
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
            border=ft.border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST),
            border_radius=10,
            divider_thickness=1,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
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
        self.rowRequests = ft.ResponsiveRow(
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
        self.btnAddRequest = ft.FilledButton(
            text="新規作成",
            tooltip="新規作成 (Shift+Alt+N)",
            icon=ft.Icons.ADD_CARD_OUTLINED,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=self.on_click_add_request,
        )

        filtered_users = os.getenv("RMX_FILTERED_IAAS_USERS", self.FILTERED_IAAS_USERS_DEFAULT).strip('"').strip('\'').split(",")
        filtered_users = list(map(lambda s: s.strip(), filtered_users))
        iaas_users = AWXApiHelper.get_users(
            self.session.get("awx_url"),
            self.session.get("awx_loginid"),
            self.session.get("awx_password"),
            filtered_users,
        )
        # iaas_users = []  # for DEBUG
        iaas_user_items = []
        for iaas_user in iaas_users:
            iaas_user_items.append(
                ft.PopupMenuItem(
                    icon=ft.Icons.ACCOUNT_CIRCLE_OUTLINED,
                    text=iaas_user["username"],
                    on_click=self.on_change_request_iaas_user,
                )
            )

        popup_menu_items = []
        match self.session.get("user_role"):
            case UserRole.ADMIN_ROLE:
                popup_menu_items = [
                    # ft.PopupMenuItem(icon=ft.Icons.ROCKET_LAUNCH, text="実行"),
                    ft.PopupMenuItem(
                        content=ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(
                                    icon=ft.Icons.FIBER_NEW,
                                    text=RequestStatus.START_FRIENDLY + " (Alt+Shift+I)",
                                    on_click=self.on_change_request_status,
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.Icons.APPROVAL,
                                    text=RequestStatus.APPROVED_FRIENDLY + " (Alt+Shift+P)",
                                    on_click=self.on_change_request_status,
                                ),
                                ft.PopupMenuItem(
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    text=RequestStatus.COMPLETED_FRIENDLY + " (Alt+Shift+E)",
                                    on_click=self.on_change_request_status,
                                ),
                            ],
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.MULTIPLE_STOP),
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
                                    ft.Icon(ft.Icons.ASSIGNMENT_IND_OUTLINED),
                                    ft.Text("作業担当者の変更"),
                                ],
                            ),
                        ),
                    ),
                    ft.PopupMenuItem(),  # divider
                    ft.PopupMenuItem(
                        icon=ft.Icons.DELETE,
                        text="削除 (Alt+Shift+R)",
                        on_click=self.on_selected_delete,
                    ),
                ]

            case UserRole.OPERATOR_ROLE:
                popup_menu_items = [
                    # ft.PopupMenuItem(icon=ft.Icons.ROCKET_LAUNCH, text="実行"),
                    ft.PopupMenuItem(
                        content=ft.PopupMenuButton(
                            items=[
                                ft.PopupMenuItem(
                                    icon=ft.Icons.CHECK_CIRCLE,
                                    text=RequestStatus.COMPLETED_FRIENDLY + " (Alt+Shift+E)",
                                    on_click=self.on_change_request_status,
                                ),
                            ],
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.MULTIPLE_STOP),
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
            icon=ft.Icons.ARROW_DROP_DOWN_CIRCLE_OUTLINED,
            tooltip="その他のアクション",
            disabled=True,
        )
        self.tfSearchRequestText = ParameterInputText(
            label="依頼内容または依頼IDに含まれる文字を検索",
            # width=340,
            expand=True,
            on_submit=self.on_click_search_request_text,
        )
        self.btnSearchRequestText = ft.IconButton(
            icon=ft.Icons.SEARCH,
            icon_color=ft.Colors.ON_SURFACE_VARIANT,
            on_click=self.on_click_search_request_text,
            autofocus=True,
            tooltip="検索 (Control+Enter)",
        )
        self.btnReloadRequestList = ft.IconButton(
            icon=ft.Icons.SYNC,
            icon_color=ft.Colors.ON_SURFACE_VARIANT,
            on_click=lambda e: self.refresh(),
            autofocus=True,
            tooltip="申請一覧の再読み込み (Control+Alt+R)",
        )
        range_min, range_max, request_data_count = RequestRowHelper.get_page_range(self)
        self.textRequestsRange = ft.Text(
            "{}-{} / {}".format(range_min, range_max, request_data_count)
        )
        self.btnPreviousPage = ft.IconButton(
            tooltip="前へ (Control+Shift+←)",
            icon=ft.Icons.ARROW_LEFT,
            icon_color=ft.Colors.ON_INVERSE_SURFACE,
            on_click=self.on_click_previous_page,
            disabled=True,
        )
        self.btnNextPage = ft.IconButton(
            tooltip="次へ (Control+Shift+→)",
            icon=ft.Icons.ARROW_RIGHT,
            icon_color=ft.Colors.ON_SURFACE_VARIANT,
            on_click=self.on_click_next_page,
        )

        # Content
        header = ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        formTitle,
                    ],
                ),
            ],
        )
        body = ft.Column(
            [
                ft.ResponsiveRow(
                    [
                        ft.Row(
                            col={"sm": 3},
                            controls=[
                                self.btnAddRequest,
                                self.btnActions,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                        ),
                        ft.Row(
                            col={"sm": 6},
                            controls=[
                                self.tfSearchRequestText,
                                self.btnSearchRequestText,
                                self.btnReloadRequestList,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Row(
                            col={"sm": 3},
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

        self.controls = ft.Container(
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

        formDeleteConfirm = DeleteConfirmForm(self.session, self.page)
        self.dlgDeleteConfirm = ft.AlertDialog(
            modal=True,
            # title=ft.Text("削除の確認"),
            content=formDeleteConfirm,
            actions=[
                ft.ElevatedButton("はい", tooltip="はい (Control+Shift+Y)", on_click=self.on_click_delete_request_yes),
                ft.FilledButton(
                    "キャンセル", tooltip="キャンセル (Esc)", on_click=self.on_click_delete_request_cancel
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.register_key_shortcuts()
        super().__init__(self.controls)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=lambda e: self.tfSearchRequestText.focus(),
        )
        # 申請の新規作成
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="N", shift=True, ctrl=False, alt=True, meta=False
            ),
            func=self.on_click_add_request,
        )
        # 依頼内容に含まれる文字の検索を実行
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Enter", shift=False, ctrl=True, alt=False, meta=False,
            ),
            func=self.on_click_search_request_text,
        )
        # 申請一覧の再読み込み
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="R", shift=False, ctrl=True, alt=True, meta=False,
            ),
            func=lambda e: self.refresh(),
        )
        # 申請一覧のページ送り / 次のページへ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Arrow Right", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=self.on_click_next_page,
        )
        # 申請一覧のページ送り / 前のページへ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Arrow Left", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=self.on_click_previous_page,
        )
        # 申請の状態の変更 => 申請中
        status_text = RequestStatus.START_FRIENDLY + " (Alt+Shift+I)"
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="I", shift=True, ctrl=False, alt=True, meta=False,
            ),
            func=lambda e, status_text=status_text: self.on_change_request_status(status_text=status_text),
        )
        # 申請の状態の変更 => 承認済み
        status_text = RequestStatus.APPROVED_FRIENDLY + " (Alt+Shift+P)"
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="P", shift=True, ctrl=False, alt=True, meta=False,
            ),
            func=lambda e, status_text=status_text: self.on_change_request_status(status_text=status_text),
        )
        # 申請の状態の変更 => 作業完了
        status_text = RequestStatus.COMPLETED_FRIENDLY + " (Alt+Shift+E)"
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="E", shift=True, ctrl=False, alt=True, meta=False,
            ),
            func=lambda e, status_text=status_text: self.on_change_request_status(status_text=status_text),
        )
        # 申請の削除
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="R", shift=True, ctrl=False, alt=True, meta=False,
            ),
            func=self.on_selected_delete,
        )

        max_row_shortcuts = min(10, len(self.dtRequests.rows))
        # 申請の編集
        for row_index in range(0, max_row_shortcuts):
            request_id = self.dtRequests.rows[row_index].cells[self.REQUEST_ID_COLUMN_NUMBER].content.value
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key=f"{row_index}", shift=True, ctrl=True, alt=False, meta=False,
                ),
                func=lambda e, request_id=request_id: self.on_request_edit_open(request_id=request_id),
            )
        # 申請の選択・選択解除
        for selected_index in range(0, max_row_shortcuts):
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key=f"{selected_index}", shift=True, ctrl=False, alt=True, meta=False,
                ),
                func=lambda e, selected_index=selected_index: self.on_request_row_select(selected_index=selected_index),
            )

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # 申請の新規作成
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="N", shift=True, ctrl=False, alt=True, meta=False
            ),
        )
        # 依頼内容に含まれる文字の検索を実行
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Enter", shift=False, ctrl=True, alt=False, meta=False,
            ),
        )
        # 申請一覧の再読み込み
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="R", shift=False, ctrl=True, alt=True, meta=False,
            ),
        )
        # 申請一覧のページ送り / 次のページへ
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Arrow Right", shift=True, ctrl=True, alt=False, meta=False,
            ),
        )
        # 申請一覧のページ送り / 前のページへ
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Arrow Left", shift=True, ctrl=True, alt=False, meta=False,
            ),
        )
        # 申請の状態の変更 => 申請中
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="I", shift=True, ctrl=False, alt=True, meta=False,
            ),
        )
        # 申請の状態の変更 => 承認済み
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="P", shift=True, ctrl=False, alt=True, meta=False,
            ),
        )
        # 申請の状態の変更 => 作業完了
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="E", shift=True, ctrl=False, alt=True, meta=False,
            ),
        )
        # 申請の削除
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="R", shift=True, ctrl=False, alt=True, meta=False,
            ),
        )
        # 申請の編集
        for row_index in range(0, 10):
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key=str(row_index), shift=True, ctrl=True, alt=False, meta=False,
                ),
            )
        # 申請の選択・選択解除
        for row_index in range(0, 10):
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key=str(row_index), shift=True, ctrl=False, alt=True, meta=False,
                ),
            )

    @abc.abstractmethod
    def get_query_filters(self):
        pass

    @Logging.func_logger
    def activate_action_button(self):
        # １件以上の申請が選択されていて、申請者以外のロールである場合、アクションメニューを有効化
        self.btnActions.disabled = True
        if self.session.get("user_role") != UserRole.USER_ROLE:
            for row in self.dtRequests.rows:
                if row.selected:
                    self.btnActions.disabled = False
                    break
        self.btnActions.update()

    @Logging.func_logger
    def deactivate_action_button(self):
        self.btnActions.disabled = True
        self.btnActions.update()

    @Logging.func_logger
    def open_delete_confirm_dialog(self):
        self.page.open(self.dlgDeleteConfirm)
        self.dlgDeleteConfirm.open = True
        self.page.update()

    @Logging.func_logger
    def open_add_request_dialog(self):
        SessionHelper.clean_request_from_session(self.session)
        wzdNewRequest = NewRequestWizard(self.session, self.page, self.refresh)
        wzdNewRequest.open_wizard()

    @Logging.func_logger
    def open_edit_request_dialog(self):
        wzdEditRequest = EditRequestWizard(
            session=self.session,
            page=self.page,
            parent_refresh_func=self.refresh,
        )
        wzdEditRequest.open_wizard()

    @Logging.func_logger
    def refresh(self):
        RequestRowHelper.refresh_data_rows(self)
        RequestRowHelper.refresh_page_indicator(self)
        self.btnActions.disabled = True
        self.btnActions.update()

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
    def on_change_request_status(self, e=None, status_text=None):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        if self.btnActions.disabled: return

        # キーボードショートカットから呼ばれた場合、
        # status_textにセットされている値を変更したいステータスの代わりに利用する
        status_text = status_text if status_text is not None else e.control.text
        if status_text == RequestStatus.START_FRIENDLY + " (Alt+Shift+I)":
            request_status = RequestStatus.START
        elif status_text == RequestStatus.APPROVED_FRIENDLY + " (Alt+Shift+P)":
            request_status = RequestStatus.APPROVED
        elif status_text == RequestStatus.COMPLETED_FRIENDLY + " (Alt+Shift+E)":
            request_status = RequestStatus.COMPLETED
        else:
            request_status = ""
        self._unlock_form_controls()
        RequestRowHelper.update_selected_request_status(self, request_status)

    @Logging.func_logger
    def on_change_request_iaas_user(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self._unlock_form_controls()
        RequestRowHelper.update_selected_request_iaas_user(self, e.control.text)

    @Logging.func_logger
    def on_click_heading_column(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self._unlock_form_controls()
        RequestRowHelper.sort_column(self, self.session, e.control.label.value)
        self.deactivate_action_button()

    @Logging.func_logger
    def on_selected_delete(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        if self.btnActions.disabled: return
        self._save_keyboard_shortcuts()
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # 削除確認時に”はい”を選択
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Y", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_delete_request_yes,
        )
        # 削除確認時に”キャンセル”を選択
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Escape", shift=False, ctrl=False, alt=False, meta=False
            ),
            func=self.on_click_delete_request_cancel,
        )
        self._unlock_form_controls()
        self.open_delete_confirm_dialog()

    @Logging.func_logger
    def on_click_add_request(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self._unlock_form_controls()
        self.open_add_request_dialog()

    @Logging.func_logger
    def on_click_delete_request_yes(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.dlgDeleteConfirm): return
        RequestRowHelper.delete_selected_requests(self)
        self._unlock_form_controls()
        self.dlgDeleteConfirm.open = False
        self.page.update()
        self.refresh()
        self._restore_key_shortcuts()

    @Logging.func_logger
    def on_click_delete_request_cancel(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session, self.dlgDeleteConfirm): return
        self._unlock_form_controls()
        self.dlgDeleteConfirm.open = False
        self.page.update()
        self.refresh()
        self._restore_key_shortcuts()

    @Logging.func_logger
    def on_click_edit_request_save(self, e):
        self._lock_form_controls()

        if SessionHelper.logout_if_session_expired(self.page, self.session, self.dlgEditRequest): return
        RequestRowHelper.update_request(self.session)
        self._unlock_form_controls()
        self.dlgEditRequest.open = False
        self.page.update()
        self.refresh()

    @Logging.func_logger
    def on_click_next_page(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        request_data_count = RequestRowHelper.count_request_all(self)
        self._unlock_form_controls()
        if (self.data_row_offset + 1) < request_data_count:
            self.data_row_offset += self.DATA_ROW_MAX
            self.refresh()

    @Logging.func_logger
    def on_click_previous_page(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self._unlock_form_controls()
        if (self.data_row_offset + 1) > self.DATA_ROW_MAX:
            self.data_row_offset -= self.DATA_ROW_MAX
            self.refresh()

    @Logging.func_logger
    def on_click_search_request_text(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session): return
        self._unlock_form_controls()
        self.data_row_offset = 0
        self.session.set("request_text_search_string", self.tfSearchRequestText.value)
        self.refresh()

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
