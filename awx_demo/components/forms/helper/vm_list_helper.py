import flet as ft

from awx_demo.utils.logging import Logging


class VmListHelper:

    # const
    DATA_ROW_MAX = 10

    @staticmethod
    @Logging.func_logger
    def generate_vm_list_labels(vm_list_form):
        vm_list_form.textVms.value = f"選択可能な仮想マシン ({len(vm_list_form.dtVmlist.rows)}件)"
        vm_list_form.textTargetedVms.value = f"変更対象の仮想マシン ({len(vm_list_form.dtTargetedVmlist.rows)}件)"

    @staticmethod
    @Logging.func_logger
    def generate_vm_list(vm_list_form):
        # 選択可能な仮想マシンのリストを再生成
        VmListHelper.generate_vm_list_rows(
            vm_list_form=vm_list_form,
            dtVmlist=vm_list_form.dtVmlist,
            on_select_changed=vm_list_form.on_select_vmlist_row,
            on_hover_datacell=vm_list_form.on_hover_datacell,
            vms_available=vm_list_form.vms_available,
            is_targeted=False,
        )
        # 変更対象の仮想マシンのリストを再生成
        VmListHelper.generate_vm_list_rows(
            vm_list_form=vm_list_form,
            dtVmlist=vm_list_form.dtTargetedVmlist,
            on_select_changed=vm_list_form.on_select_targeted_vmlist_row,
            on_hover_datacell=vm_list_form.on_hover_datacell,
            vms_available=vm_list_form.vms_available,
            is_targeted=True,
        )

    @staticmethod
    @Logging.func_logger
    def update_vm_list(vm_list_form, dtVmlist: ft.DataTable, on_select_changed: callable, is_targeted: bool):
        # 選択された仮想マシンを変更対象に追加
        VmListHelper.append_checked_vms_to_vm_list(
            vm_list_form=vm_list_form,
            dtVmlist=dtVmlist,
            on_select_changed=on_select_changed,
        )

        if is_targeted:
            # 変更対象から削除した仮想マシンをセッションから削除
            if len(vm_list_form.target_vms_array) > 0:
                vm_list_form.target_vms_array = list(
                    set(vm_list_form.target_vms_array) - set(vm_list_form.targeted_vmlist_checked)
                )
            else:
                assert False, "TARGET_VMS not in session.get('job_options')"
        else:
            # 変更対象の仮想マシンをセッションに追加
            if len(vm_list_form.target_vms_array) > 0:
                vm_list_form.target_vms_array.extend(vm_list_form.vmlist_checked)
            else:
                vm_list_form.target_vms_array = vm_list_form.vmlist_checked

        # 仮想マシンのリストを再生成
        VmListHelper.generate_vm_list(vm_list_form)
        VmListHelper.generate_vm_list_labels(vm_list_form)

        # 仮想マシンリストのチェック状態をクリア
        VmListHelper.uncheck_all_vms_from_vmlists(vm_list_form)

        # 各コントロールを再描画
        vm_list_form.dtVmlist.update()
        vm_list_form.dtTargetedVmlist.update()
        vm_list_form.textVms.update()
        vm_list_form.textTargetedVms.update()

    @staticmethod
    @Logging.func_logger
    def uncheck_all_vms_from_vmlists(vm_list_form):
        vm_list_form.vmlist_checked = []
        vm_list_form.targeted_vmlist_checked = []
        for row in vm_list_form.dtVmlist.rows:
            row.selected = False
        for row in vm_list_form.dtTargetedVmlist.rows:
            row.selected = False

    @staticmethod
    @Logging.func_logger
    def append_checked_vms_to_vm_list(vm_list_form, dtVmlist: ft.DataTable, on_select_changed):
        available_vm_names = [vm.name for vm in vm_list_form.vms_available]
        for vm_name in vm_list_form.vmlist_checked:
            if vm_name in available_vm_names:
                # 該当する仮想マシン名のオブジェクトを取得
                vm = next((vm for vm in vm_list_form.vms_available if vm.name == vm_name), None)
                dtVmlist.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm.name,
                                        tooltip=f"仮想マシン名: {vm.name}, ホスト名: {vm.hostname},\nvCenter: {vm.vcenter}, システム識別子: {vm.vm_folder}",
                                    ),
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm.hostname,
                                    )
                                ),
                            ),
                        ],
                        on_select_changed=on_select_changed,
                    )
                )
        dtVmlist.rows.sort(key=lambda x: x.cells[0].content.content.value)

    @staticmethod
    @Logging.func_logger
    def generate_vm_list_rows(
        vm_list_form,
        dtVmlist: ft.DataTable,
        on_select_changed,
        on_hover_datacell,
        vms_available: dict,
        # is_targeted: 選択対象の仮想マシンか変更対象の仮想マシンかどうかを指定
        is_targeted: bool,
    ):
        dtVmlist.rows = []
        # 選択可能な仮想マシンが0件の場合、処理せず終了する
        if vms_available is None:
            return

        for vm in vms_available:
            targeted = True if vm_list_form.target_vms_array and vm.name in vm_list_form.target_vms_array else False
            if targeted is is_targeted:
                vm_tooltip = f"仮想マシン名: {vm.name}, ホスト名: {vm.hostname},\nvCenter: {vm.vcenter}, システム識別子: {vm.vm_folder}"
                dtVmlist.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm.name,
                                        tooltip=vm_tooltip,
                                    ),
                                    on_hover=on_hover_datacell,
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm.hostname,
                                    ),
                                ),
                            ),
                        ],
                        on_select_changed=on_select_changed,
                    )
                )
        dtVmlist.rows.sort(key=lambda x: x.cells[0].content.content.value)

    @staticmethod
    @Logging.func_logger
    def get_vms_from_dtVmlist(dtVmlist: ft.DataTable):
        vms = []
        for row in dtVmlist.rows:
            if row.cells[0].content.value:
                vms.append(row.cells[0].content.value)
        return vms
