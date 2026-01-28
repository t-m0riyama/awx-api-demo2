import flet as ft

from awx_demo.components.forms.helper.vm_list_helper import VmListHelper
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.wizards.base_wizard_card import BaseWizardCardError
from awx_demo.utils.logging import Logging
from awx_demo.vcenter_client_bridge.vlb_simple_client import VlbSimpleClient
from awx_demo.vcenter_client_bridge.vlb_simple_client import VlbSimpleClientError


class SelectTargetVmTabForm(ft.Card):

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
        page,
        height=CONTENT_HEIGHT,
        width=CONTENT_WIDTH,
        body_height=BODY_HEIGHT,
        on_change_vms_hook: callable = None,
        lock_form_controls: callable = None,
        unlock_form_controls: callable = None,
    ):
        self.session = session
        self.page = page
        self.on_change_vms_hook = on_change_vms_hook
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self._lock_form_controls = lock_form_controls
        self._unlock_form_controls = unlock_form_controls

        # target_vmsを配列に変換
        if "target_vms" in self.session.get("job_options"):
            self.target_vms_array = [x.strip() for x in self.session.get("job_options")["target_vms"].split(",")]
            # 先頭の仮想マシン１台のみを対象とする
            self.target_vms_array = [self.target_vms_array[0]]
        else:
            self.target_vms_array = []

        try:
            # vCenter Lookup Bridge Clientの設定を生成
            vlb_configuration = VlbSimpleClient.generate_configuration()
            # vCenter Lookup Bridge ClientのAPIクライアントを生成
            self.api_client = VlbSimpleClient.get_api_client(configuration=vlb_configuration)
        except VlbSimpleClientError as e:
            raise BaseWizardCardError("vCenter参照機能の呼び出しに失敗しました。")

        # controls
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
            heading_row_height=25,
            data_row_max_height=50,
            sort_column_index=0,
            sort_ascending=True,
            checkbox_horizontal_margin=15,
            # on_sort_func=self.on_click_heading_column,
            width=self.VM_LIST_MAX_WIDTH,
            on_select_all=self.on_select_all_dtVmlist,
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
            single_vm_list=True,
        )
        # 変更対象として選択されている仮想マシンを、チェック済みにする
        for row in self.dtVmlist.rows:
            if row.cells[0].content.content.value in self.target_vms_array:
                row.selected = True
            else:
                row.selected = False

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

        # Content
        body = ft.Column(
            [
                # formDescription,
                ft.ResponsiveRow(
                    [
                        ft.Column(
                            col={"sm": 24},
                            controls=[
                                self.textVms,
                                ft.SelectionArea(self.vm_list),
                            ],
                            scroll=ft.ScrollMode.AUTO,
                            # expand=True,
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                    ],
                    columns=24,
                ),
            ],
            height=self.body_height,
        )

        self.controls = ft.Container(
            ft.SelectionArea(
                content=ft.Column(
                    [
                        body,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                )
            ),
            width=self.content_width,
            height=self.content_height,
            padding=30,
        )
        self.register_key_shortcuts()
        super().__init__(self.controls)

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        # keyboard_shortcut_manager.register_key_shortcut(
        #     key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
        #     func=lambda e: self.dtVmlist.focus(),
        # )
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
        self._register_key_shortcuts_rows()

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        if self.page:
            keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
            # autofocus=Trueである、最初のコントロールにフォーカスを移動する
            # keyboard_shortcut_manager.unregister_key_shortcut(
            #     key_set=keyboard_shortcut_manager.create_key_set(key="F", shift=True, ctrl=False, alt=True, meta=False),
            # )
            # ログへのキーボードショートカット一覧出力
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(key="Z", shift=True, ctrl=False, alt=True, meta=False),
            )
            self._unregister_key_shortcuts_rows()

    @Logging.func_logger
    def _register_key_shortcuts_rows(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        max_row_shortcuts = min(10, len(self.dtVmlist.rows))
        # 仮想マシンの選択・選択解除
        for selected_index in range(0, max_row_shortcuts):
            keyboard_shortcut_manager.register_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key=f"{selected_index}",
                    shift=True,
                    ctrl=False,
                    alt=False,
                    meta=False,
                ),
                func=lambda e, selected_index=selected_index: self.on_select_vmlist_row(selected_index=selected_index),
            )

    @Logging.func_logger
    def _unregister_key_shortcuts_rows(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # 仮想マシンの選択・選択解除
        for row_index in range(0, 10):
            keyboard_shortcut_manager.unregister_key_shortcut(
                key_set=keyboard_shortcut_manager.create_key_set(
                    key=str(row_index),
                    shift=True,
                    ctrl=False,
                    alt=False,
                    meta=False,
                ),
            )

    @Logging.func_logger
    def on_hover_datacell(self, e):
        vm_name = e.control.content.value
        vm = next((vm for vm in self.vms_available if vm.name == vm_name), None)
        # 仮想マシンの詳細情報を取得
        if not hasattr(vm, "disk_devices"):
            try:
                vm_detail = VlbSimpleClient.get_vm(
                    api_client=self.api_client, vcenter=vm.vcenter, vm_instance_uuid=vm.instance_uuid
                )
            except VlbSimpleClientError as e:
                raise BaseWizardCardError("vCenter参照機能の呼び出しに失敗しました。")
            tooltip_str = f"仮想マシン名: {vm_detail.name}, ホスト名: {vm_detail.hostname},\n"
            tooltip_str += f"vCenter: {vm_detail.vcenter}, システム識別子: {vm_detail.vm_folder}, \n"
            tooltip_str += f"電源状態: {vm_detail.power_state}, CPUコア数: {vm_detail.num_cpu}, メモリ容量(GB): {int(vm_detail.memory_size_mb / 1024)}, IPアドレス: {vm_detail.ip_address}"
            e.control.content.tooltip = tooltip_str
            # コントロールが初期化前の場合、エラーが発生するため、try-exceptで処理
            try:
                e.control.content.update()
            except:
                pass

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

        try:
            # 選択可能な仮想マシンのリストを取得
            if vcenter != "" and vcenter != "指定なし":
                # vCenterが指定されている場合は、vCenterとシステム識別子を指定して仮想マシンのリストを取得
                vms_available = VlbSimpleClient.get_vms_by_vm_folders(
                    api_client=self.api_client,
                    vcenter=vcenter,
                    system_ids=system_ids_array,
                )
            else:
                # vCenterが指定されていない場合は、システム識別子のみを指定して仮想マシンのリストを取得
                vms_available = VlbSimpleClient.get_vms_by_vm_folders(
                    api_client=self.api_client,
                    system_ids=system_ids_array,
                )
        except VlbSimpleClientError as e:
            raise BaseWizardCardError("vCenter参照機能の呼び出しに失敗しました。")

        return vms_available

    @Logging.func_logger
    def refresh_vms_available(self):
        self.vms_available = self._get_vms_available()
        VmListHelper.generate_vm_list_rows(
            vm_list_form=self,
            dtVmlist=self.dtVmlist,
            on_select_changed=self.on_select_vmlist_row,
            on_hover_datacell=self.on_hover_datacell,
            vms_available=self.vms_available,
            is_targeted=False,
            single_vm_list=True,
        )
        # 変更対象として選択されている仮想マシンを、チェック済みにする
        for row in self.dtVmlist.rows:
            if row.cells[0].content.content.value in self.target_vms_array:
                row.selected = True
            else:
                row.selected = False

        self.textVms.value = f"選択可能な仮想マシン ({len(self.dtVmlist.rows)}件)"
        self.textVms.update()
        self.dtVmlist.update()

    @Logging.func_logger
    def on_select_vmlist_row(self, e=None, selected_index=None):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session):
            return

        # キーボードショートカットから呼ばれた場合、
        # selected_indexにセットされている値を申請一覧のインデックスの代わりに利用する
        if selected_index is not None:
            selected_vm_name = self.dtVmlist.rows[selected_index].cells[0].content.content.value
            selected_hostname = self.dtVmlist.rows[selected_index].cells[1].content.content.value
        else:
            selected_vm_name = e.control.cells[0].content.content.value
            selected_hostname = e.control.cells[1].content.content.value

        # 対象の仮想マシンを選択・選択解除、それ以外の仮想マシンは選択解除
        for row in self.dtVmlist.rows:
            if (
                row.cells[0].content.content.value == selected_vm_name
                and row.cells[1].content.content.value == selected_hostname
            ):
                row.selected = not row.selected
                if row.selected:
                    self.target_vms_array = [selected_vm_name]
                else:
                    self.target_vms_array = []
            else:
                row.selected = False

        self.dtVmlist.update()
        self._change_vms_hook()
        self._unlock_form_controls()

    @Logging.func_logger
    def on_hover_datacell(self, e):
        vm_name = e.control.content.value
        shortcut_index = VmListHelper.get_shortcut_index_from_tooltip(e.control.content.tooltip)
        vm = next((vm for vm in self.vms_available if vm.name == vm_name), None)
        # 仮想マシンの詳細情報を取得
        if not hasattr(vm, "disk_devices"):
            try:
                tooltip_str = VmListHelper.generate_vm_detail_tooltip(
                    vm_object=vm, api_client=self.api_client, is_targeted=False, shortcut_index=shortcut_index
                )
            except Exception as e:
                raise BaseWizardCardError("vCenter参照機能の呼び出しに失敗しました。")
        else:
            tooltip_str = VmListHelper.remove_shortcut_from_tooltip(e.control.content.tooltip)

        # ツールチップにショートカットを追加
        tooltip_str += VmListHelper.generate_shortcut_tooltip(is_targeted=False, shortcut_index=shortcut_index)

        # 仮想マシンの詳細情報を正常に取得できた場合、ツールチップを更新する
        if tooltip_str:
            e.control.content.tooltip = tooltip_str
        # コントロールが初期化前の場合、エラーが発生するため、try-exceptで処理
        try:
            e.control.content.update()
        except:
            pass

    @Logging.func_logger
    def on_select_all_dtVmlist(self, e):
        # 全行の選択・選択解除を無効化
        pass

    @Logging.func_logger
    def _change_vms_hook(self):
        self.session.get("job_options")["target_vms"] = ",".join(sorted(self.target_vms_array))
        self.on_change_vms_hook()
