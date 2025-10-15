import flet as ft

from awx_demo.components.types.user_role import UserRole
from awx_demo.utils.logging import Logging
from awx_demo.vcenter_client_bridge.vlb_simple_client import VlbSimpleClient


class SelectTargetVCenterTabForm(ft.Card):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    SYSTEM_IDS_LENGTH_MAX = 30

    def __init__(
        self,
        session,
        height=CONTENT_HEIGHT,
        width=CONTENT_WIDTH,
        body_height=BODY_HEIGHT,
        on_change_vcenter_or_system_ids=None,
        lock_form_controls=None,
        unlock_form_controls=None,
    ):
        self.session = session
        self.on_change_vcenter_or_system_ids = on_change_vcenter_or_system_ids
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self._lock_form_controls = lock_form_controls
        self._unlock_form_controls = unlock_form_controls

        # vCenter Lookup Bridge Clientの設定を生成
        vlb_configuration = VlbSimpleClient.generate_configuration()
        # vCenter Lookup Bridge ClientのAPIクライアントを生成
        api_client = VlbSimpleClient.get_api_client(configuration=vlb_configuration)

        # system_idsを配列に変換
        if "system_ids" in self.session.get("job_options"):
            self.system_ids_array = [x.strip() for x in self.session.get("job_options")["system_ids"].split(",")]
        else:
            self.system_ids_array = []

        # controls
        # 選択可能なvCenterの決定
        vsphere_vcenters = VlbSimpleClient.get_vcenters(api_client=api_client)
        vcenter_options = [ft.dropdown.Option("指定なし")]
        for vsphere_vcenter in vsphere_vcenters:
            vcenter_options.append(
                ft.dropdown.Option(f"{vsphere_vcenter.description.strip()} | {vsphere_vcenter.name.strip()}")
            )

        # デフォルトのvCenterの名前を設定
        default_vcenter = "指定なし"
        if "vsphere_vcenter" in self.session.get("job_options"):
            for vsphere_vcenter in vsphere_vcenters:
                if (
                    self.session.get("job_options")["vsphere_vcenter"]
                    == f"{vsphere_vcenter.description.strip()} | {vsphere_vcenter.name.strip()}"
                ):
                    default_vcenter = self.session.get("job_options")["vsphere_vcenter"]
                    break

        # vCenterの指定
        self.dropVcenter = ft.Dropdown(
            label="vCenter名(*)",
            value=default_vcenter,
            options=vcenter_options,
            hint_text="仮想マシンの稼働するvCenter名を指定します。",
            on_change=self.on_change_vcenter,
            expand=True,
            autofocus=True,
        )

        # 選択可能なシステム識別子の決定
        all_system_ids = VlbSimpleClient.get_vm_folders(api_client=api_client)
        selected_system_ids = self.system_ids_array
        self.system_id_options = []

        for system_id in all_system_ids:
            # 選択済みのシステム識別子については、チェックをつける
            checked = True if system_id.name in selected_system_ids else False
            self.system_id_options.append(
                ft.dropdown.Option(
                    key=system_id.name,
                    content=ft.Checkbox(
                        label=system_id.name,
                        value=checked,
                        on_change=self.on_change_system_ids,
                    ),
                )
            )

        # システム識別子の指定
        self.dropSystemIds = ft.Dropdown(
            label=self._generate_drop_system_ids_label(),
            options=self.system_id_options,
            hint_text="仮想マシンのシステム識別子を指定します。",
            expand=True,
        )

        vcenter_system_ids = [
            ft.Column(
                col={"sm": 6},
                controls=[
                    self.dropVcenter,
                ],
            ),
            ft.Column(
                col={"sm": 6},
                controls=[
                    self.dropSystemIds,
                ],
            ),
        ]

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = True if self.session.get("user_role") == UserRole.USER_ROLE else False

        # Content
        body = ft.Column(
            [
                ft.ResponsiveRow(vcenter_system_ids),
            ],
            height=self.body_height,
            disabled=change_disabled,
        )

        controls = ft.Container(
            ft.Column(
                [
                    body,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            width=self.content_width,
            height=self.content_height,
            padding=30,
        )
        super().__init__(controls)

    @Logging.func_logger
    def _generate_drop_system_ids_label(self):
        if len(self.system_ids_array) > 0:
            label_text = ", ".join(sorted(self.system_ids_array))
            if len(label_text) > self.SYSTEM_IDS_LENGTH_MAX:
                label_text = label_text[: self.SYSTEM_IDS_LENGTH_MAX] + "..."
            return f"システム識別子(＊): {label_text}"
        else:
            return "システム識別子(＊):"

    @Logging.func_logger
    def _is_valid_vcenter_and_system_ids(self):
        if (
            self.session.get("job_options")["vsphere_vcenter"] == ""
            or self.session.get("job_options")["vsphere_vcenter"] == "指定なし"
        ):
            return False
        if self.session.get("job_options")["system_ids"] == "":
            return False
        return True

    @Logging.func_logger
    def on_change_vcenter(self, e):
        self.session.get("job_options")["vsphere_vcenter"] = e.control.value
        # 変更対象の仮想マシンのリストを更新する関数を呼び出す
        if self._is_valid_vcenter_and_system_ids():
            self._lock_form_controls()
            self.on_change_vcenter_or_system_ids()
            self._unlock_form_controls()

    @Logging.func_logger
    def on_change_system_ids(self, e):
        # システム識別子の追加/削除
        if e.control.value:
            if e.control.label not in self.system_ids_array:
                self.system_ids_array.append(e.control.label)
        else:
            if e.control.label in self.system_ids_array:
                self.system_ids_array.remove(e.control.label)
        self.dropSystemIds.label = self._generate_drop_system_ids_label()
        self.dropSystemIds.update()

        # セッションを更新
        if len(self.system_ids_array) > 0:
            self.session.get("job_options")["system_ids"] = ",".join(self.system_ids_array)
        else:
            self.session.get("job_options")["system_ids"] = ""

        # 変更対象の仮想マシンのリストを更新する関数を呼び出す
        if self._is_valid_vcenter_and_system_ids():
            self._lock_form_controls()
            self.on_change_vcenter_or_system_ids()
            self._unlock_form_controls()
