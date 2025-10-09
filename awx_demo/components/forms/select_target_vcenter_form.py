import os

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.types.user_role import UserRole
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.utils.logging import Logging
from awx_demo.vcenter_client_bridge.vlb_simple_client import VlbSimpleClient


class SelectTargetVcenterForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    SYSTEM_IDS_LENGTH_MAX = 30

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
        formTitle = FormTitle("変更対象のvCenter選択", "vCenterとシステム識別子の指定")
        formDescription = FormDescription(
            "変更対象の仮想マシンが稼働するvCenterを指定します。システム識別子は作業の担当者または管理者以外は変更不要できます。＊は入力/選択が必須の項目です。"
        )

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
            label="vCenter名(＊)",
            value=default_vcenter,
            options=vcenter_options,
            hint_text="稼働するvCenter名を指定します。",
            expand=True,
            autofocus=True,
            on_change=self.on_change_vcenter,
        )

        # 選択可能なシステム識別子の決定
        all_system_ids = VlbSimpleClient.get_vm_folders(api_client=api_client)
        selected_system_ids = self.system_ids_array
        self.system_id_options = []

        for system_id in all_system_ids:
            # 申請者ロールの場合
            if self.session.get("user_role") == UserRole.USER_ROLE:
                # ユーザの所属するシステム識別子以外は、選択肢から除外する
                if system_id.name not in self.session.get("system_ids"):
                    continue
                # ユーザの所属するシステム識別子は、選択肢に含め、チェックをつける
                self.system_id_options.append(
                    ft.dropdown.Option(
                        key=system_id.name,
                        content=ft.Checkbox(
                            label=system_id.name,
                            value=True,
                            on_change=self.on_change_system_ids,
                        ),
                    )
                )
            # 申請者ロール以外の場合
            else:
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

        # 初回の読み込み時、チェックされたシステム識別子をシステム識別子の配列に追加する
        if len(self.system_ids_array) == 0:
            for system_id_option in self.system_id_options:
                if system_id_option.content.value:
                    self.system_ids_array.append(system_id_option.content.label)

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

        if self.dropVcenter.value == "" or self.dropVcenter.value == "指定なし":
            btn_next_disabled = True
        else:
            if len(self.system_ids_array) > 0:
                btn_next_disabled = False
            else:
                btn_next_disabled = True

        self.btnNext = ft.FilledButton(
            "次へ",
            tooltip="次へ (Shift+Alt+N)",
            on_click=self.on_click_next,
            disabled=btn_next_disabled,
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
                ft.ResponsiveRow(vcenter_system_ids),
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
            func=lambda e: self.dropVcenter.focus(),
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(key="Z", shift=True, ctrl=False, alt=True, meta=False),
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
    def on_change_vcenter(self, e):
        if e.control.value == "" or e.control.value == "指定なし":
            self.btnNext.disabled = True
            self.btnNext.update()
        else:
            if len(self.system_ids_array) > 0:
                self.btnNext.disabled = False
                self.btnNext.update()
        self.session.get("job_options")["vsphere_vcenter"] = e.control.value

    @Logging.func_logger
    def on_change_system_ids(self, e):
        # システム識別子の追加/削除
        if e.control.value:
            if not e.control.label in self.system_ids_array:
                self.system_ids_array.append(e.control.label)
        else:
            if e.control.label in self.system_ids_array:
                self.system_ids_array.remove(e.control.label)
        self.dropSystemIds.label = self._generate_drop_system_ids_label()
        self.dropSystemIds.update()

        # セッションと次へボタンの有効/無効を更新
        if len(self.system_ids_array) > 0:
            self.session.get("job_options")["system_ids"] = ",".join(self.system_ids_array)
            if self.dropVcenter.value == "" or self.dropSystemIds.value == "指定なし":
                self.btnNext.disabled = True
            else:
                self.btnNext.disabled = False
        else:
            self.session.get("job_options")["system_ids"] = ""
            self.btnNext.disabled = True
        self.btnNext.update()

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
    def on_click_next(self, e):
        # 変更対象のvCenterが指定されていない場合は、処理せず終了する
        if self.dropVcenter.value == "" or self.dropSystemIds.value == "指定なし":
            return

        self._lock_form_controls()
        self.session.get("job_options")["vsphere_vcenter"] = self.dropVcenter.value
        self.session.get("job_options")["system_ids"] = ",".join(self.system_ids_array)
        self.step_change_next(e)
        self._unlock_form_controls()
