import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.utils.logging import Logging
from awx_demo.vcenter_client_bridge.vlb_simple_client import VlbSimpleClient
from awx_demo.components.forms.helper.vm_list_helper import VmListHelper


class SelectTargetVmsForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_LIST_MAX_HEIGHT = 240
    VM_LIST_MAX_WIDTH = 320
    VM_LIST_PADDING_SIZE = 5

    def __init__(
        self,
        session,
        page: ft.Page,
        height=CONTENT_HEIGHT,
        width=CONTENT_WIDTH,
        body_height=BODY_HEIGHT,
        step_change_next=None,
        step_change_previous=None,
        step_change_cancel=None,
    ):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel

        # target_vmsを配列に変換
        if "target_vms" in self.session.get("job_options"):
            self.target_vms_array = [x.strip() for x in self.session.get("job_options")["target_vms"].split(",")]
        else:
            self.target_vms_array = []

        # vCenter Lookup Bridge Clientの設定を生成
        vlb_configuration = VlbSimpleClient.generate_configuration()
        # vCenter Lookup Bridge ClientのAPIクライアントを生成
        self.api_client = VlbSimpleClient.get_api_client(configuration=vlb_configuration)

        # controls
        formTitle = FormTitle("変更対象の仮想マシン選択", "仮想マシンの指定")
        formDescription = FormDescription(
            "変更対象の仮想マシンを指定します。選択可能な仮想マシンが表示されない場合、適切なvCenterとシステム識別子を再度指定して下さい。"
        )

        # 選択可能な仮想マシンのリスト
        self.dtVmlist = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("仮想マシン名")),
                ft.DataColumn(ft.Text("ホスト名")),
            ],
            rows=[],
            show_checkbox_column=True,
            show_bottom_border=True,
            border=ft.border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST),
            border_radius=10,
            divider_thickness=1,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            column_spacing=60,
            # heading_row_height=25,
            # data_row_max_height=50,
            heading_row_height=25,
            data_row_max_height=50,
            sort_column_index=0,
            sort_ascending=True,
            checkbox_horizontal_margin=15,
            # on_sort_func=self.on_click_heading_column,
            width=self.VM_LIST_MAX_WIDTH,
        )

        # 選択可能な仮想マシンのリストを取得
        self.vms_available = self._get_vms_available()

        VmListHelper.generate_vm_list_rows(
            vm_list_form=self,
            dtVmlist=self.dtVmlist,
            on_select_changed=self.on_select_vmlist_row,
            on_hover_datacell=self.on_hover_datacell,
            vms_available=self.vms_available,
            is_targeted=False,
        )

        self.textVms = ft.Text(
            f"選択可能な仮想マシン ({len(self.dtVmlist.rows)}件)",
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        self.vm_list = ft.Container(
            content=ft.Row(
                controls=[
                    self.dtVmlist,
                ],
                expand=True,
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
                scroll=ft.ScrollMode.AUTO,
                tight=True,
            ),
            height=self.VM_LIST_MAX_HEIGHT,
            padding=ft.padding.all(self.VM_LIST_PADDING_SIZE),
        )

        self.btnAddVm = ft.FilledButton(
            ">",
            tooltip="変更対象に追加",
            on_click=self.on_click_add_vm,
            disabled=False if len(self.dtVmlist.rows) > 0 else True,
        )
        self.btnRemoveVm = ft.FilledButton(
            "<",
            tooltip="変更対象から除外",
            on_click=self.on_click_remove_vm,
            disabled=(
                False
                if "target_vms" in self.session.get("job_options")
                and len(self.session.get("job_options")["target_vms"]) > 0
                else True
            ),
        )

        # 変更対象の仮想マシンのリスト
        self.dtTargetedVmlist = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("仮想マシン名")),
                ft.DataColumn(ft.Text("ホスト名")),
            ],
            rows=[],
            show_checkbox_column=True,
            show_bottom_border=True,
            border=ft.border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST),
            border_radius=10,
            divider_thickness=1,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            column_spacing=60,
            # heading_row_height=25,
            # data_row_max_height=50,
            heading_row_height=25,
            data_row_max_height=50,
            sort_column_index=0,
            sort_ascending=True,
            checkbox_horizontal_margin=15,
            # on_sort_func=self.on_click_heading_column,
            width=self.VM_LIST_MAX_WIDTH,
        )
        VmListHelper.generate_vm_list_rows(
            vm_list_form=self,
            dtVmlist=self.dtTargetedVmlist,
            on_select_changed=self.on_select_targeted_vmlist_row,
            on_hover_datacell=self.on_hover_datacell,
            vms_available=self.vms_available,
            is_targeted=True,
        )

        self.textTargetedVms = ft.Text(
            f"変更対象の仮想マシン ({len(self.dtTargetedVmlist.rows)}件)",
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        self.targeted_vm_list = ft.Container(
            content=ft.Row(
                controls=[
                    self.dtTargetedVmlist,
                ],
                expand=True,
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
                scroll=ft.ScrollMode.AUTO,
                tight=True,
            ),
            height=self.VM_LIST_MAX_HEIGHT,
            padding=ft.padding.all(self.VM_LIST_PADDING_SIZE),
        )

        self.btnNext = ft.FilledButton(
            "次へ",
            tooltip="次へ (Shift+Alt+N)",
            on_click=self.on_click_next,
            disabled=False if "target_vms" in self.session.get("job_options") else True,
        )
        self.btnPrev = ft.ElevatedButton("戻る", tooltip="戻る (Shift+Alt+P)", on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            "キャンセル",
            tooltip="キャンセル (Shift+Alt+X)",
            on_click=self.on_click_cancel,
        )

        # チェック済みの選択された仮想マシン
        self.vmlist_checked = []
        # チェック済みの変更対象の仮想マシン
        self.targeted_vmlist_checked = []

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"sm": 11},
                            controls=[
                                self.textVms,
                                ft.SelectionArea(self.vm_list),
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            # expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        ft.Column(
                            col={"sm": 2},
                            controls=[
                                ft.Row(controls=[], height=60),
                                self.btnAddVm,
                                self.btnRemoveVm,
                            ],
                            # expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        ft.Column(
                            col={"sm": 11},
                            controls=[
                                self.textTargetedVms,
                                ft.SelectionArea(self.targeted_vm_list),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    columns=24,
                ),
            ],
            height=self.body_height,
        )
        footer = ft.Row(
            [
                self.btnCancel,
                self.btnPrev,
                self.btnNext,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.controls = ft.Container(
            ft.SelectionArea(
                content=ft.Column(
                    [
                        header,
                        body,
                        ft.Divider(),
                        footer,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ),
            width=self.content_width,
            height=self.content_height,
            padding=30,
        )
        super().__init__(self.controls)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
            func=lambda e: self.panelListVms.focus(),
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Z",
                shift=True,
                ctrl=False,
                alt=True,
                meta=False,
            ),
            func=lambda e: keyboard_shortcut_manager.dump_key_shortcuts(),
        )
        super().register_key_shortcuts()

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        if self.page:
            keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
            # autofocus=Trueである、最初のコントロールにフォーカスを移動する
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
            )
            # ログへのキーボードショートカット一覧出力
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(key="Z", shift=True, ctrl=False, alt=True, meta=False),
            )
            super().unregister_key_shortcuts()

    # @Logging.func_logger
    # def get_query_filters(self):
    #     filters = []
    #     if self.session.get('user_role') == UserRole.USER_ROLE:
    #         match self.session.get("selected_indicator"):
    #             case _:
    #                 filters.append(IaasRequestHelper.get_filter_request_status([RequestStatus.APPLYING_FAILED]))
    #         filters.append(IaasRequestHelper.get_filter_request_user(self.session.get('awx_loginid')))
    #     else:
    #         match self.session.get("selected_indicator"):
    #             case _:
    #                 filters.append(IaasRequestHelper.get_filter_request_status([RequestStatus.APPLYING_FAILED]))

    #     return filters

    @Logging.func_logger
    def _get_vms_available(self):
        # システム識別子の配列を初期化
        if "system_ids" in self.session.get("job_options"):
            system_ids_array = [x.strip() for x in self.session.get("job_options")["system_ids"].split(",")]
        else:
            system_ids_array = []

        # vCenter名をセッションから取得
        if "vsphere_vcenter" in self.session.get("job_options"):
            if len(self.session.get("job_options")["vsphere_vcenter"].split("|")) == 2:
                vcenter = self.session.get("job_options")["vsphere_vcenter"].split("|")[1].strip()
            else:
                vcenter = self.session.get("job_options")["vsphere_vcenter"]
        else:
            vcenter = ""

        # 選択可能な仮想マシンのリストを取得
        if vcenter != "":
            vms_available = VlbSimpleClient.get_vms_by_vm_folders(
                api_client=self.api_client,
                vcenter=vcenter,
                system_ids=system_ids_array,
            )
        else:
            vms_available = []

        return vms_available

    @Logging.func_logger
    def refresh_vms_available(self):
        self.vms_available = self._get_vms_available()
        VmListHelper.update_vm_list(
            self, dtVmlist=self.dtVmlist, on_select_changed=self.on_select_vmlist_row, is_targeted=False
        )
        VmListHelper.update_vm_list(
            self, dtVmlist=self.dtTargetedVmlist, on_select_changed=self.on_select_targeted_vmlist_row, is_targeted=True
        )

    @Logging.func_logger
    def on_select_vmlist_row(self, e=None, selected_index=None):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session):
            return

        # キーボードショートカットから呼ばれた場合、
        # selected_indexにセットされている値を申請一覧のインデックスの代わりに利用する
        if selected_index is not None:
            self.dtVmlist.rows[selected_index].selected = not self.dtVmlist.rows[selected_index].selected
            self.dtVmlist.rows[selected_index].update()
        else:
            e.control.selected = not e.control.selected
            e.control.update()

        checked_vms = []
        for row in self.dtVmlist.rows:
            if row.selected:
                checked_vms.append(row.cells[0].content.content.value)
        self.vmlist_checked = checked_vms
        self._unlock_form_controls()

    @Logging.func_logger
    def on_select_targeted_vmlist_row(self, e=None, selected_index=None):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session):
            return

        # キーボードショートカットから呼ばれた場合、
        # selected_indexにセットされている値を申請一覧のインデックスの代わりに利用する
        if selected_index is not None:
            self.dtTargetedVmlist.rows[selected_index].selected = not self.dtTargetedVmlist.rows[
                selected_index
            ].selected
            self.dtTargetedVmlist.rows[selected_index].update()
        else:
            e.control.selected = not e.control.selected
            e.control.update()

        checked_vms = []
        for row in self.dtTargetedVmlist.rows:
            if row.selected:
                checked_vms.append(row.cells[0].content.content.value)
        self.targeted_vmlist_checked = checked_vms
        # self.activate_action_button()
        self._unlock_form_controls()

    @Logging.func_logger
    def on_hover_datacell(self, e):
        vm_name = e.control.content.value
        vm = next((vm for vm in self.vms_available if vm.name == vm_name), None)
        # 仮想マシンの詳細情報を取得
        if not hasattr(vm, "disk_devices"):
            tooltip_str = VmListHelper.generate_vm_detail_tooltip(vm, self.api_client)
            e.control.content.tooltip = tooltip_str
            # コントロールが初期化前の場合、エラーが発生するため、try-exceptで処理
            try:
                e.control.content.update()
            except:
                pass

    @Logging.func_logger
    def on_click_add_vm(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session):
            return

        # チェックされた仮想マシンが0件の場合、処理せず終了する
        if len(self.vmlist_checked) == 0:
            self._unlock_form_controls()
            return

        # 仮想マシンのリストを更新
        VmListHelper.update_vm_list(
            vm_list_form=self,
            dtVmlist=self.dtTargetedVmlist,
            on_select_changed=self.on_select_targeted_vmlist_row,
            is_targeted=False,
        )

        # 変更対象から除外ボタンの無効化を解除
        self.btnRemoveVm.disabled = False
        self.btnRemoveVm.update()

        # 選択対象の仮想マシンが0件の場合、追加ボタンを無効化
        if len(self.dtVmlist.rows) == 0:
            self.btnAddVm.disabled = True
            self.btnAddVm.update()

        # 変更対象の仮想マシンが1件以上の場合、次へボタンを無効化
        if len(self.dtTargetedVmlist.rows) == 0:
            self.btnNext.disabled = True
        else:
            self.btnNext.disabled = False
        self.btnNext.update()
        self._unlock_form_controls()

    @Logging.func_logger
    def on_click_remove_vm(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session):
            return

        # チェックされた仮想マシンが0件の場合、処理せず終了する
        if len(self.targeted_vmlist_checked) == 0:
            self._unlock_form_controls()
            return

        # 仮想マシンのリストを更新
        VmListHelper.update_vm_list(
            vm_list_form=self,
            dtVmlist=self.dtVmlist,
            on_select_changed=self.on_select_vmlist_row,
            is_targeted=True,
        )

        # 変更対象に追加ボタンの無効化を解除
        self.btnAddVm.disabled = False
        self.btnAddVm.update()

        # 変更対象の仮想マシンが0件の場合、除外ボタンを無効化
        if len(self.dtTargetedVmlist.rows) == 0:
            self.btnRemoveVm.disabled = True
            self.btnRemoveVm.update()

        # 変更対象の仮想マシンが1件以上の場合、次へボタンを無効化
        if len(self.dtTargetedVmlist.rows) == 0:
            self.btnNext.disabled = True
        else:
            self.btnNext.disabled = False
        self.btnNext.update()
        self._unlock_form_controls()

    @Logging.func_logger
    def on_change_vms(self, e):
        if e.control.value == "":
            self.btnNext.disabled = True
        else:
            self.btnNext.disabled = False
        self.btnNext.update()

    @Logging.func_logger
    def on_click_previous(self, e):
        self._lock_form_controls()
        if len(self.target_vms_array) > 0:
            self.session.get("job_options")["target_vms"] = ",".join(sorted(self.target_vms_array))
        else:
            # 変更対象の仮想マシンが指定されていない場合は、セッションの値を””にする
            self.session.get("job_options")["target_vms"] = ""
        self._unlock_form_controls()
        self.step_change_previous(e)

    @Logging.func_logger
    def on_click_next(self, e):
        # 変更対象の仮想マシンが指定されていない場合は、処理せず終了する
        if len(self.target_vms_array) == 0:
            return

        self._lock_form_controls()
        self.session.get("job_options")["target_vms"] = ",".join(sorted(self.target_vms_array))

        # 変更対象に選択された１台目の仮想マシンのCPUコア数とメモリ容量をセッションにセット
        available_vm_names = [vm.name for vm in self.vms_available]
        for vm_name in sorted(self.target_vms_array):
            if vm_name in sorted(available_vm_names):
                # 該当する仮想マシン名のオブジェクトを取得
                vm = next((vm for vm in self.vms_available if vm.name == vm_name), None)

                # セッションに保存されているデフォルト値と変更対象の仮想マシンのCPUコア数とメモリ容量が異なる場合は、セッションの値をクリア
                if self.session.contains_key("vcpus_default") and self.session.get("vcpus_default") != vm.num_cpu:
                    if "vcpus" in self.session.get("job_options"):
                        deleted_vcpus = self.session.get("job_options").pop("vcpus")
                if self.session.contains_key("memory_gb_default") and self.session.get("memory_gb_default") != int(
                    vm.memory_size_mb / 1024
                ):
                    if "memory_gb" in self.session.get("job_options"):
                        deleted_memory_gb = self.session.get("job_options").pop("memory_gb")

                # セッションにデフォルト値をセット（設定変更前のデフォルト値として利用するため）
                self.session.set("vcpus_default", vm.num_cpu)
                self.session.set("memory_gb_default", int(vm.memory_size_mb / 1024))
                break

        self.step_change_next(e)
        self._unlock_form_controls()
