import flet as ft
from distutils.util import strtobool

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.components.wizards.base_wizard_card import BaseWizardCardError
from awx_demo.utils.logging import Logging
from awx_demo.vcenter_client_bridge.vlb_simple_client import VlbSimpleClient
from awx_demo.vcenter_client_bridge.vlb_simple_client import VlbSimpleClientError
from awx_demo.components.forms.helper.vm_snapshot_list_helper import VmSnapshotListHelper
from awx_demo.components.forms.helper.vm_snapshot_helper import VmSnapshotHelper


class SelectTargetVmSnapshotForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VM_SNAPSHOT_LIST_MAX_HEIGHT = 240
    VM_SNAPSHOT_LIST_MAX_WIDTH = 680
    VM_SNAPSHOT_LIST_PADDING_SIZE = 5
    TARGET_VM_SNAPSHOT_ID_NOTOUND = -1
    TARGET_VM_SNAPSHOT_NAME_NOTFOUND = ""
    DEFAULT_SORT_ASCENDING = False

    def __init__(
        self,
        session,
        page: ft.Page,
        height=CONTENT_HEIGHT,
        width=CONTENT_WIDTH,
        body_height=BODY_HEIGHT,
        sub_title="スナップショットの指定",
        description="操作対象のスナップショットを指定します。",
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

        # セッション中にスナップショットIDとスナップショット名がない場合は、デフォルト値をセット
        if not "target_vm_snapshot_id" in self.session.get("job_options"):
            self.session.get("job_options")["target_vm_snapshot_id"] = self.TARGET_VM_SNAPSHOT_ID_NOTOUND
        if not "target_vm_snapshot_name" in self.session.get("job_options"):
            self.session.get("job_options")["target_vm_snapshot_name"] = self.TARGET_VM_SNAPSHOT_NAME_NOTFOUND

        try:
            # vCenter Lookup Bridge Clientの設定を生成
            vlb_configuration = VlbSimpleClient.generate_configuration()
            # vCenter Lookup Bridge ClientのAPIクライアントを生成
            self.api_client = VlbSimpleClient.get_api_client(configuration=vlb_configuration)
        except VlbSimpleClientError as e:
            raise BaseWizardCardError("vCenter参照機能の呼び出しに失敗しました。")

        # controls
        formTitle = FormTitle("操作対象のスナップショット選択", f"{sub_title}")
        formDescription = FormDescription(
            f"{description}選択可能なスナップショットが表示されない場合、適切な仮想マシンを再度指定して下さい。"
        )

        # スナップショットのリストを生成
        self.dtVmSnapshots = VmSnapshotListHelper.generate_vm_snapshot_table(
            session=self.session,
            width=self.VM_SNAPSHOT_LIST_MAX_WIDTH,
            show_checkbox_column=True,
            checkbox_horizontal_margin=15,
            heading_row_height=25,
            data_row_max_height=50,
            on_sort_func=self.on_click_heading_column,
            on_select_all_func=self.on_select_all_dtVmSnapshots,
        )

        # 仮想マシン中のスナップショット一覧を取得
        self.vm_snapshots_available = self._get_vm_snapshots_available()

        VmSnapshotListHelper.generate_vm_snapshot_list_rows(
            dtVmSnapshots=self.dtVmSnapshots,
            on_select_changed=self.on_select_vm_snapshot_list_row,
            vm_snapshots_available=self.vm_snapshots_available,
            target_vm_multiple=(
                bool(strtobool(str(self.session.get("job_options")["target_vm_multiple"])))
                if "target_vm_multiple" in self.session.get("job_options")
                else False
            ),
        )

        # 変更対象として選択されている仮想マシンを、チェック済みにする
        target_vm_snapshot_id = (
            self.session.get("job_options")["target_vm_snapshot_id"]
            if "target_vm_snapshot_id" in self.session.get("job_options")
            else self.TARGET_VM_SNAPSHOT_ID_NOTOUND
        )
        for row in self.dtVmSnapshots.rows:
            if row.cells[1].content.content.value == target_vm_snapshot_id:
                row.selected = True
            else:
                row.selected = False

        self.textVmSnapshots = ft.Text(
            f"選択可能なスナップショット ({len(self.dtVmSnapshots.rows)}件)",
            size=16,
            weight=ft.FontWeight.BOLD,
        )
        self.vm_snapshot_list = ft.Container(
            content=ft.Row(
                controls=[
                    self.dtVmSnapshots,
                ],
                expand=True,
                wrap=True,
                alignment=ft.MainAxisAlignment.START,
                scroll=ft.ScrollMode.AUTO,
                tight=True,
            ),
            height=self.VM_SNAPSHOT_LIST_MAX_HEIGHT,
            padding=ft.padding.all(self.VM_SNAPSHOT_LIST_PADDING_SIZE),
        )

        self.btnNext = ft.FilledButton(
            "次へ",
            tooltip="次へ (Shift+Alt+N)",
            on_click=self.on_click_next,
            disabled=(
                False
                if "target_vm_snapshot_id" in self.session.get("job_options")
                and self.session.get("job_options")["target_vm_snapshot_id"] != self.TARGET_VM_SNAPSHOT_ID_NOTOUND
                else True
            ),
        )
        self.btnPrev = ft.ElevatedButton("戻る", tooltip="戻る (Shift+Alt+P)", on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            "キャンセル",
            tooltip="キャンセル (Shift+Alt+X)",
            on_click=self.on_click_cancel,
        )

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
                            col={"sm": 24},
                            controls=[
                                self.textVmSnapshots,
                                ft.SelectionArea(self.vm_snapshot_list),
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

    @Logging.func_logger
    def _get_vm_snapshots_available(self):
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

        # 選択可能なスナップショットのリストを取得
        if vcenter != "":
            try:
                # スナップショット操作対象の仮想マシンのインスタンスUUIDを取得
                vm_instance_uuid = VlbSimpleClient.get_vm_instance_uuid_by_vm_name(
                    api_client=self.api_client,
                    vcenter=vcenter,
                    system_ids=system_ids_array,
                    vm_name=self.session.get("job_options")["target_vms"].split(",")[0],
                )
                # スナップショット操作対象の仮想マシンのスナップショットのリストを取得
                vm_snapshots = VlbSimpleClient.get_vm_snapshots(
                    api_client=self.api_client, vcenter=vcenter, vm_instance_uuid=vm_instance_uuid
                )
            except VlbSimpleClientError as e:
                raise BaseWizardCardError("vCenter参照機能の呼び出しに失敗しました。")

            if vm_snapshots:
                snapshot_tree = VmSnapshotHelper.build_snapshot_tree(snapshots=vm_snapshots)
                if "target_vm_multiple" in self.session.get("job_options") and bool(
                    strtobool(str(self.session.get("job_options")["target_vm_multiple"]))
                ):
                    vm_snapshots_available = VmSnapshotHelper.generate_snapshot_list_flat_format(
                        snapshot_tree=snapshot_tree,
                        indent=0,
                    )
                else:
                    vm_snapshots_available = VmSnapshotHelper.generate_snapshot_list_hierarchy_format(
                        snapshot_tree=snapshot_tree,
                        initial_indent=0,
                        step_indent=4,
                    )
            else:
                Logging.warning(
                    f"SNAPSHOT_NOT_FOUND: 仮想マシン{self.session.get('job_options')['target_vms'].split(',')[0]}のスナップショットが取得できませんでした。"
                )
                vm_snapshots_available = []
        else:
            vm_snapshots_available = []

        return vm_snapshots_available

    @Logging.func_logger
    def generate_confirm_text(self):
        confirm_text = "== 基本情報 ====================="
        confirm_text += "\n依頼者(アカウント): " + self.session.get("awx_loginid")
        confirm_text += "\n依頼内容: " + (
            self.session.get("request_text")
            if self.session.contains_key("request_text") and self.session.get("request_text") != ""
            else "(未指定)"
        )
        confirm_text += "\n依頼区分: " + self.session.get("request_category")
        confirm_text += "\n申請項目: " + self.session.get("request_operation")
        request_deadline = (
            self.session.get("request_deadline").strftime("%Y/%m/%d")
            if self.session.contains_key("request_deadline")
            else "(未指定)"
        )
        confirm_text += "\nリリース希望日: " + request_deadline
        confirm_text += "\n\n== 詳細情報 ====================="
        confirm_text += "\nvCenter: " + self.session.get("job_options")["vsphere_vcenter"]
        confirm_text += "\n仮想マシン: " + self.session.get("job_options")["target_vms"]
        match self.session.get("job_options")["snapshot_operation"]:
            case "take_vm_snapshot":
                confirm_text += "\nスナップショット操作: スナップショットの取得"
            case "revert_vm_snapshot":
                confirm_text += "\nスナップショット操作: スナップショットの切り戻し"
            case "remove_vm_snapshot":
                confirm_text += "\nスナップショット操作: スナップショットの削除"
            case _:
                assert False, "スナップショット操作が不正です。"
        if (
            bool(strtobool(str(self.session.get("job_options")["target_vm_multiple"])))
            or self.session.get("job_options")["snapshot_operation"] == "take_vm_snapshot"
        ):
            confirm_text += f"\nスナップショット名: {self.session.get('job_options')['target_vm_snapshot_name']}"
            confirm_text += (
                f"\nスナップショット説明: {self.session.get('job_options')['target_vm_snapshot_description']}"
            )
        else:
            confirm_text += f"\nスナップショット名: {self.session.get('job_options')['target_vm_snapshot_name']}"
            confirm_text += f"\nスナップショットID: {str(self.session.get('job_options')['target_vm_snapshot_id'])}"
        return confirm_text

    @Logging.func_logger
    def on_click_heading_column(self, e):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session):
            return

        target_vm_multiple = (
            bool(strtobool(str(self.session.get("job_options")["target_vm_multiple"])))
            if "target_vm_multiple" in self.session.get("job_options")
            else False
        )
        VmSnapshotListHelper.sort_column(
            self, self.session, e.control.label.value, target_vm_multiple=target_vm_multiple
        )
        self._unlock_form_controls()

    @Logging.func_logger
    def on_select_vm_snapshot_list_row(self, e=None, selected_index=None):
        self._lock_form_controls()
        if SessionHelper.logout_if_session_expired(self.page, self.session):
            return

        # キーボードショートカットから呼ばれた場合、
        # selected_indexにセットされている値を申請一覧のインデックスの代わりに利用する
        # if selected_index is not None:
        #     self.dtVmlist.rows[selected_index].selected = not self.dtVmlist.rows[selected_index].selected
        #     self.dtVmlist.rows[selected_index].update()
        # else:
        #     e.control.selected = not e.control.selected
        #     e.control.update()

        btn_next_disabled = True
        selected_snapshot_id = e.control.cells[1].content.content.value
        selected_snapshot_name = e.control.cells[2].content.content.value

        for row in self.dtVmSnapshots.rows:
            if (
                row.cells[1].content.content.value == selected_snapshot_id
                and row.cells[2].content.content.value == selected_snapshot_name
            ):
                row.selected = not row.selected
                if row.selected:
                    self.session.get("job_options")["target_vm_snapshot_id"] = selected_snapshot_id
                    self.session.get("job_options")["target_vm_snapshot_name"] = selected_snapshot_name.strip().replace(
                        "└", ""
                    )
                    btn_next_disabled = False
                else:
                    self.session.get("job_options")["target_vm_snapshot_id"] = self.TARGET_VM_SNAPSHOT_ID_NOTOUND
                    self.session.get("job_options")["target_vm_snapshot_name"] = self.TARGET_VM_SNAPSHOT_NAME_NOTFOUND
                    btn_next_disabled = True
            else:
                row.selected = False

        self.dtVmSnapshots.update()
        self.btnNext.disabled = btn_next_disabled
        self.btnNext.update()
        self._unlock_form_controls()

    @Logging.func_logger
    def on_select_all_dtVmSnapshots(self, e):
        # 全行の選択・選択解除を無効化
        pass

    @Logging.func_logger
    def on_click_previous(self, e):
        self._lock_form_controls()
        self.step_change_previous(e)
        self._unlock_form_controls()

    @Logging.func_logger
    def on_click_next(self, e):
        # 変更対象のスナップショットが指定されていない場合は、処理せず終了する
        if not "target_vm_snapshot_id" in self.session.get("job_options"):
            return
        if self.session.get("job_options")["target_vm_snapshot_id"] == self.TARGET_VM_SNAPSHOT_ID_NOTOUND:
            return

        self._lock_form_controls()
        self.session.set("confirm_text", self.generate_confirm_text())
        Logging.info("JOB_OPTIONS: " + str(self.session.get("job_options")))
        self.step_change_next(e)
        self._unlock_form_controls()
