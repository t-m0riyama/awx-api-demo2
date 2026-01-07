# from ctypes import alignment
from distutils.util import strtobool

import flet as ft

from awx_demo.utils.logging import Logging

# from awx_demo.vcenter_client_bridge.vlb_simple_client import VlbSimpleClient


class VmSnapshotListHelper:

    @staticmethod
    @Logging.func_logger
    def _generate_vm_snapshot_list_labels(vm_snapshot_list_form):
        vm_snapshot_list_form.textVmSnapshots.value = (
            f"選択可能なスナップショット ({len(vm_snapshot_list_form.dtVmSnapshots.rows)}件)"
        )

    @staticmethod
    @Logging.func_logger
    def _generate_vm_snapshot_list(vm_snapshot_list_form, target_vm_multiple: bool):
        # 選択可能なスナップショットのリストを再生成
        VmSnapshotListHelper.generate_vm_snapshot_list_rows(
            dtVmSnapshots=vm_snapshot_list_form.dtVmSnapshots,
            on_select_changed=vm_snapshot_list_form.on_select_vm_snapshot_list_row,
            vm_snapshots_available=vm_snapshot_list_form.vm_snapshots_available,
            target_vm_multiple=target_vm_multiple,
        )

    @staticmethod
    @Logging.func_logger
    def update_vm_snapshot_list(vm_snapshot_list_form, target_vm_multiple: bool):
        # スナップショットのリストを再生成
        VmSnapshotListHelper._generate_vm_snapshot_list(vm_snapshot_list_form, target_vm_multiple)
        VmSnapshotListHelper._generate_vm_snapshot_list_labels(vm_snapshot_list_form)

        # スナップショットリストのチェック状態をクリア
        VmSnapshotListHelper.uncheck_all_vm_snapshots_from_vmlists(vm_snapshot_list_form)

        # 各コントロールを再描画
        vm_snapshot_list_form.dtVmSnapshots.update()
        vm_snapshot_list_form.textVmSnapshots.update()

    @staticmethod
    @Logging.func_logger
    def uncheck_all_vm_snapshots_from_vmlists(vm_snapshot_list_form):
        for row in vm_snapshot_list_form.dtVmSnapshots.rows:
            row.selected = False

    @staticmethod
    @Logging.func_logger
    def generate_vm_snapshot_table(
        session,
        width: int = 400,
        show_checkbox_column=False,
        checkbox_horizontal_margin: int = 15,
        heading_row_height: int = 25,
        data_row_max_height: int = 50,
        sort_column_index: int = 2,
        column_spacing: int = 10,
        is_sort_ascending: bool = True,
        on_sort_func: callable = None,
        on_select_all_func: callable = None,
    ) -> ft.DataTable:
        # 列の定義
        #   ソート用にSORT_ID列を作成（非表示）
        #   複数仮想マシンを対象にするときは、ID列,説明列を非表示にする
        if "target_vm_multiple" in session.get("job_options") and bool(
            strtobool(str(session.get("job_options")["target_vm_multiple"]))
        ):
            vm_snapshot_columns = [
                ft.DataColumn(ft.Text("SORT_ID"), visible=False),
                ft.DataColumn(ft.Text("ID"), visible=False),
                ft.DataColumn(ft.Text("スナップショット名"), on_sort=on_sort_func),
                ft.DataColumn(ft.Text("最新"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("作成日時"), on_sort=on_sort_func),
                ft.DataColumn(ft.Text("説明"), visible=False),
            ]
            # 作成日時列(visible=Falseではない列の2番目)をソート対象にする
            sort_column_index = 1
        else:
            vm_snapshot_columns = [
                ft.DataColumn(ft.Text("SORT_ID"), visible=False),
                ft.DataColumn(ft.Text("ID"), on_sort=on_sort_func),
                ft.DataColumn(ft.Text("スナップショット名"), on_sort=on_sort_func),
                ft.DataColumn(ft.Text("最新"), heading_row_alignment=ft.MainAxisAlignment.CENTER),
                ft.DataColumn(ft.Text("作成日時"), on_sort=on_sort_func),
                ft.DataColumn(ft.Text("説明"), on_sort=on_sort_func),
            ]
            # SORT_ID列をソート対象にする
            sort_column_index = 0

        dtVmSnapshots = ft.DataTable(
            columns=vm_snapshot_columns,
            rows=[],
            show_checkbox_column=show_checkbox_column,
            show_bottom_border=True,
            border=ft.border.all(2, ft.Colors.SURFACE_CONTAINER_HIGHEST),
            border_radius=10,
            divider_thickness=1,
            heading_row_color=ft.Colors.SURFACE_CONTAINER_HIGHEST,
            column_spacing=column_spacing,
            heading_row_height=heading_row_height,
            data_row_max_height=data_row_max_height,
            sort_column_index=sort_column_index,
            sort_ascending=is_sort_ascending,
            checkbox_horizontal_margin=checkbox_horizontal_margin,
            on_select_all=on_select_all_func,
            width=width,
        )
        return dtVmSnapshots

    @staticmethod
    @Logging.func_logger
    def generate_vm_snapshot_list_rows(
        dtVmSnapshots: ft.DataTable,
        on_select_changed: callable,
        vm_snapshots_available: dict,
        target_vm_multiple: bool = False,
    ):
        dtVmSnapshots.rows = []
        # 選択可能なスナップショットが0件の場合、処理せず終了する
        if len(vm_snapshots_available) == 0:
            return

        latest_vm_snapshot = sorted(vm_snapshots_available, key=lambda x: x.create_time, reverse=True)[0]
        latest_vm_snapshot_id = latest_vm_snapshot.id
        for vm_snapshot in vm_snapshots_available:
            sort_id = 0
            latest_icon = VmSnapshotListHelper._vm_snapshot_latest_to_icon(
                vm_snapshot=vm_snapshot, latest_vm_snapshot_id=latest_vm_snapshot_id
            )
            if target_vm_multiple:
                sort_id = sort_id + 1
                vm_snapshot_name_trimmed = vm_snapshot.name.strip().replace("└", "")
                vm_snapshot_tooltip = f"スナップショット名: {vm_snapshot_name_trimmed}, \n"
                vm_snapshot_tooltip += f"作成日時: {vm_snapshot.create_time}"
                dtVmSnapshots.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        sort_id,
                                    ),
                                ),
                                visible=False,
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm_snapshot.id,
                                        tooltip=vm_snapshot_tooltip,
                                    ),
                                ),
                                visible=False,
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm_snapshot.name,
                                        tooltip=vm_snapshot_tooltip,
                                    ),
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=latest_icon,
                                    alignment=ft.alignment.center,
                                    expand=True,
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm_snapshot.create_time,
                                        tooltip=vm_snapshot_tooltip,
                                    ),
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm_snapshot.description,
                                        tooltip=vm_snapshot_tooltip,
                                    ),
                                ),
                                visible=False,
                            ),
                        ],
                        on_select_changed=on_select_changed,
                    )
                )
            else:
                sort_id = sort_id + 1
                vm_snapshot_name_trimmed = vm_snapshot.name.strip().replace("└", "")
                vm_snapshot_tooltip = f"ID: {vm_snapshot.id}, \n"
                vm_snapshot_tooltip += f"スナップショット名: {vm_snapshot_name_trimmed}, \n"
                vm_snapshot_tooltip += f"仮想マシン名: {vm_snapshot.vm_name}, \n"
                vm_snapshot_tooltip += f"作成日時: {vm_snapshot.create_time}, \n"
                vm_snapshot_tooltip += f"説明: {vm_snapshot.description}"
                dtVmSnapshots.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        sort_id,
                                    ),
                                ),
                                visible=False,
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm_snapshot.id,
                                        tooltip=vm_snapshot_tooltip,
                                    ),
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm_snapshot.name,
                                        tooltip=vm_snapshot_tooltip,
                                    ),
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=latest_icon,
                                    alignment=ft.alignment.center,
                                    expand=True,
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm_snapshot.create_time,
                                        tooltip=vm_snapshot_tooltip,
                                    ),
                                ),
                            ),
                            ft.DataCell(
                                content=ft.Container(
                                    content=ft.Text(
                                        vm_snapshot.description,
                                        tooltip=vm_snapshot_tooltip,
                                    ),
                                ),
                            ),
                        ],
                        on_select_changed=on_select_changed,
                    )
                )
        dtVmSnapshots.rows.sort(key=lambda x: x.cells[0].content.content.value)

    @staticmethod
    @Logging.func_logger
    def sort_column(vm_snapshot_list_form, session, column_label, target_vm_multiple: bool = False):
        session.set("sort_target_vm_snapshot_column", column_label)
        column_index_in_row = 0
        # ソート対象が同じ列の場合、昇順と降順を逆転させる
        if session.get("sort_target_vm_snapshot_column") == session.get(
            "sort_target_vm_snapshot_column_old"
        ) or not session.get("sort_target_vm_snapshot_column_old"):
            vm_snapshot_list_form.dtVmSnapshots.sort_ascending = not vm_snapshot_list_form.dtVmSnapshots.sort_ascending

        if target_vm_multiple:
            match column_label:
                case "スナップショット名":
                    vm_snapshot_list_form.dtVmSnapshots.sort_column_index = 0
                    column_index_in_row = 2
                case "最新":
                    vm_snapshot_list_form.dtVmSnapshots.sort_column_index = 1
                    column_index_in_row = 3
                case "作成日時":
                    vm_snapshot_list_form.dtVmSnapshots.sort_column_index = 2
                    column_index_in_row = 4
        else:
            match column_label:
                case "ID":
                    vm_snapshot_list_form.dtVmSnapshots.sort_column_index = 0
                    column_index_in_row = 1
                case "スナップショット名":
                    vm_snapshot_list_form.dtVmSnapshots.sort_column_index = 1
                    column_index_in_row = 2
                case "最新":
                    vm_snapshot_list_form.dtVmSnapshots.sort_column_index = 2
                    column_index_in_row = 3
                case "作成日時":
                    vm_snapshot_list_form.dtVmSnapshots.sort_column_index = 3
                    column_index_in_row = 4
                case "説明":
                    vm_snapshot_list_form.dtVmSnapshots.sort_column_index = 4
                    column_index_in_row = 5
        session.set("sort_target_vm_snapshot_column_old", column_label)
        vm_snapshot_list_form.dtVmSnapshots.rows.sort(
            key=lambda x: x.cells[column_index_in_row].content.content.value,
            reverse=not vm_snapshot_list_form.dtVmSnapshots.sort_ascending,
        )
        vm_snapshot_list_form.dtVmSnapshots.update()

    @staticmethod
    def _vm_snapshot_latest_to_icon(vm_snapshot, latest_vm_snapshot_id: int):
        # 最新のスナップショットであればアイコンを返し、それ以外はNoneを返す
        if vm_snapshot.id == latest_vm_snapshot_id:
            return ft.Icon(
                name=ft.Icons.STAR_ROUNDED, color=ft.Colors.PRIMARY, size=18, tooltip="最新のスナップショット"
            )
        else:
            return None
