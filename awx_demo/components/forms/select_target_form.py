import os

import flet as ft

from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.compounds.parameter_input_text import ParameterInputText
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.types.user_role import UserRole
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.utils.logging import Logging


class SelectTargetForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    VMS_LENGTH_MAX = 120
    VSPHERE_CLUSTERS_DEFAULT = 'cluster-1'

    def __init__(self, session, page: ft.Page, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.page = page
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel

        # controls
        formTitle = FormTitle('変更対象の選択', 'クラスタと仮想マシンの指定')
        formDescription = FormDescription('変更対象の仮想マシンと稼働するクラスタを指定します。クラスタは作業時に担当者が指定します。＊は入力/選択が必須の項目です。')

        # 申請者ロールの場合は、変更できないようにする
        change_disabled = (
            True if self.session.get("user_role") == UserRole.USER_ROLE else False
        )

        # 選択可能なクラスタの決定
        vsphere_clusters = os.getenv('RMX_VSPHERE_CLUSTERS', self.VSPHERE_CLUSTERS_DEFAULT).strip('"').strip('\'')
        cluster_options = [ft.dropdown.Option("指定なし")]
        for vsphere_cluster in vsphere_clusters.split(","):
            cluster_options.append(ft.dropdown.Option(vsphere_cluster.strip()))

        # 仮想マシンの指定
        self.dropCluster = ft.Dropdown(
            label='クラスタ',
            value=self.session.get('job_options')['vsphere_cluster'] if 'vsphere_cluster' in self.session.get('job_options') else '指定なし',
            options=cluster_options,
            hint_text='仮想マシンの稼働するクラスタ名を指定します。',
            autofocus=True,
            disabled=change_disabled,
        )
        self.tfVms = ParameterInputText(
            value=self.session.get('job_options')[
                'target_vms'] if 'target_vms' in self.session.get('job_options') else '',
            label='仮想マシン名(＊)',
            hint_text='仮想マシンを指定します。複数の仮想マシンは、「,」で区切ることで指定できます。',
            max_length=self.VMS_LENGTH_MAX,
            on_change=self.on_change_vms,
            on_submit=self.on_click_next,
        )
        self.btnNext = ft.FilledButton(
            '次へ', tooltip='次へ (Cotrol+Shift+N)', on_click=self.on_click_next,
            disabled=False if 'target_vms' in self.session.get('job_options') else True)
        self.btnPrev = ft.ElevatedButton(
            '戻る', tooltip='戻る (Cotrol+Shift+P)', on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            'キャンセル', tooltip='キャンセル (Cotrol+Shift+X)', on_click=self.on_click_cancel)

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
                self.dropCluster,
                self.tfVms,
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
            ft.Column(
                [
                    header,
                    body,
                    ft.Divider(),
                    footer,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
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
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=lambda e: self.dropCluster.focus(),
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=lambda e: keyboard_shortcut_manager.dump_key_shortcuts(),
        )
        super().register_key_shortcuts()

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # autofocus=Trueである、最初のコントロールにフォーカスを移動する
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="F", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        super().unregister_key_shortcuts()

    @Logging.func_logger
    def on_change_vms(self, e):
        if e.control.value == '':
            self.btnNext.disabled = True
        else:
            self.btnNext.disabled = False
        self.btnNext.update()

    @Logging.func_logger
    def on_click_next(self, e):
        if self.tfVms.value == '': return
        self._lock_form_controls()
        self.session.get('job_options')['vsphere_cluster'] = self.dropCluster.value
        self.session.get('job_options')['target_vms'] = self.tfVms.value
        self._unlock_form_controls()
        self.step_change_next(e)
