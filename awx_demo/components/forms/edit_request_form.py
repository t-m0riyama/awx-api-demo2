import flet as ft

from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.forms.edit_tab.manage_info_tab_form import ManageInfoTabForm
from awx_demo.components.forms.edit_tab.request_common_info_tab_form import RequestCommonInfoTabForm
from awx_demo.components.forms.edit_tab.select_target_tab_form import SelectTargetTabForm
from awx_demo.components.forms.edit_tab.set_vm_cpu_tab_form import SetVmCpuTabForm
from awx_demo.components.forms.edit_tab.set_vm_memory_tab_form import SetVmMemoryTabForm
from awx_demo.components.forms.edit_tab.set_vm_start_stop_tab_form import SetVmStartStopTabForm
from awx_demo.components.keyboard_shortcut_manager import KeyboardShortcutManager
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_category import RequestOperation
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.db_helper.types.vm_start_stop import VmStartStop
from awx_demo.utils.logging import Logging


class EditRequestForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 540
    CONTENT_WIDTH = 800
    BODY_HEIGHT = 380

    def __init__(self, session, page: ft.Page, request_id=None, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, click_execute_func=None, click_duplicate_func=None, click_save_func=None, click_cancel_func=None):
        self.session = session
        self.page = page
        self.request_id = request_id
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = click_execute_func
        self.step_change_cancel = click_cancel_func
        self.click_duplicate_func = click_duplicate_func
        self.click_save_func = click_save_func

        self.tab_content_height = self.content_height - 80
        self.tab_content_width = self.content_width
        self.tab_body_height = self.body_height - 80

        db_session = db.get_db()
        SessionHelper.load_request_to_session_from_db(
            self.session, db_session, self.request_id)
        request_operation = IaasRequestHelper.get_request(db_session, self.request_id).request_operation
        db_session.close()

        # controls
        if self.session.get('user_role') == UserRole.USER_ROLE:
            formTitle = FormTitle('申請の詳細', '')
        else:
            formTitle = FormTitle('申請の編集', '')

        # overlayを利用する可能性があるコントロールは、あらかじめインスタンスを作成する
        match request_operation:
            case RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY:
                self.formCommonInfo = RequestCommonInfoTabForm(
                    self.session,
                    self.page,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.formSelectTarget = SelectTargetTabForm(
                    self.session,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.formSetVmCpu = SetVmCpuTabForm(
                    self.session,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.formSetVmMemory = SetVmMemoryTabForm(
                    self.session,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.formManageInfo = ManageInfoTabForm(
                    self.session,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.tabRequest = ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(
                            tab_content=ft.Text('共通', tooltip='共通 (Cotrol+Shift+G)'),
                            content=self.formCommonInfo,
                        ),
                        ft.Tab(
                            tab_content=ft.Text('変更対象', tooltip='変更対象 (Cotrol+Shift+T)'),
                            content=self.formSelectTarget,
                        ),
                        ft.Tab(
                            tab_content=ft.Text('CPU', tooltip='CPU (Cotrol+Shift+C)'),
                            content=self.formSetVmCpu,
                        ),
                        ft.Tab(
                            tab_content=ft.Text('メモリ', tooltip='メモリ (Cotrol+Shift+M)'),
                            content=self.formSetVmMemory,
                        ),
                        ft.Tab(
                            tab_content=ft.Text('管理情報', tooltip='管理情報 (Cotrol+Shift+A)'),
                            content=self.formManageInfo,
                        ),
                    ],
                    scrollable=True,
                    expand=1,
                )
            case RequestOperation.VM_START_OR_STOP_FRIENDLY:
                self.formCommonInfo = RequestCommonInfoTabForm(
                    self.session,
                    self.page,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.formSelectTarget = SelectTargetTabForm(
                    self.session,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.formStartStop = SetVmStartStopTabForm(
                    self.session,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.formManageInfo = ManageInfoTabForm(
                    self.session,
                    self.tab_content_height,
                    self.tab_content_width,
                    self.tab_body_height,
                )
                self.tabRequest = ft.Tabs(
                    selected_index=0,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(
                            tab_content=ft.Text('共通', tooltip='共通 (Cotrol+Shift+G)'),
                            content=self.formCommonInfo,
                        ),
                        ft.Tab(
                            tab_content=ft.Text('変更対象', tooltip='変更対象 (Cotrol+Shift+T)'),
                            content=self.formSelectTarget,
                        ),
                        ft.Tab(
                            tab_content=ft.Text('起動/停止', tooltip='変更対象 (Cotrol+Shift+B)'),
                            content=self.formStartStop,
                        ),
                        ft.Tab(
                            tab_content=ft.Text('管理情報', tooltip='管理情報 (Cotrol+Shift+A)'),
                            content=self.formManageInfo,
                        ),
                    ],
                    scrollable=True,
                    expand=1,
                )
        change_disabled = True if self.session.get('user_role') == UserRole.USER_ROLE else False
        is_execute_disabled = self.session.get('request_status') not in [
            RequestStatus.APPROVED, RequestStatus.COMPLETED]
        self.btnExecute = ft.ElevatedButton(
            '実行', tooltip='実行 (Cotrol+Shift+N)', on_click=self.on_click_next, disabled=(is_execute_disabled or change_disabled))
        self.btnSave = ft.ElevatedButton(
            '保存', tooltip='保存 (Cotrol+Shift+S)', on_click=self.on_click_save, disabled=change_disabled)
        self.btnDuplicate = ft.ElevatedButton(
            '複製', tooltip='複製 (Cotrol+Shift+D)', on_click=self.on_click_duplicate, disabled=change_disabled)
        self.btnCancel = ft.FilledButton(
            '閉じる', tooltip='閉じる (Cotrol+Shift+X)', on_click=self.on_click_cancel)

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                self.tabRequest,
            ],
            height=self.body_height,
        )
        footer = ft.Row(
            [
                self.btnCancel,
                self.btnDuplicate,
                self.btnSave,
                self.btnExecute,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.controls = ft.Container(
            ft.Column(
                [
                    header,
                    body,
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
    def generate_confirm_text(self):
        db_session = db.get_db()
        request_operation = IaasRequestHelper.get_request(db_session, self.request_id).request_operation
        db_session.close()
        confirm_text = '== 基本情報 ====================='
        match request_operation:
            case RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY:
                confirm_text += '\n依頼者(アカウント): ' + self.session.get('awx_loginid')
                confirm_text += '\n依頼内容: ' + (self.session.get('request_text') if self.session.contains_key(
                    'request_text') and self.session.get('request_text') != '' else '(未指定)')
                confirm_text += '\n依頼区分: ' + self.session.get('request_category')
                confirm_text += '\n申請項目: ' + self.session.get('request_operation')
                request_deadline = self.session.get('request_deadline').strftime(
                    '%Y/%m/%d') if self.session.contains_key('request_deadline') else '(未指定)'
                confirm_text += '\nリリース希望日: ' + request_deadline
                confirm_text += '\n\n== 詳細情報 ====================='
                confirm_text += '\nクラスタ: ' + \
                    self.session.get('job_options')['vsphere_cluster']
                confirm_text += '\n仮想マシン: ' + \
                    self.session.get('job_options')['target_vms']
                if str(self.session.get('job_options')['change_vm_cpu_enabled']) == 'True':
                    confirm_text += '\nCPUコア数: ' + \
                        str(self.session.get('job_options')['vcpus'])
                if str(self.session.get('job_options')['change_vm_memory_enabled']) == 'True':
                    confirm_text += '\nメモリ容量(GB): ' + str(self.session.get('job_options')['memory_gb'])
            case RequestOperation.VM_START_OR_STOP_FRIENDLY:
                confirm_text += '\n依頼者(アカウント): ' + self.session.get('awx_loginid')
                confirm_text += '\n依頼内容: ' + (self.session.get('request_text') if self.session.contains_key(
                    'request_text') and self.session.get('request_text') != '' else '(未指定)')
                confirm_text += '\n依頼区分: ' + self.session.get('request_category')
                confirm_text += '\n申請項目: ' + self.session.get('request_operation')
                request_deadline = self.session.get('request_deadline').strftime(
                    '%Y/%m/%d') if self.session.contains_key('request_deadline') else '(未指定)'
                confirm_text += '\nリリース希望日: ' + request_deadline
                confirm_text += '\n\n== 詳細情報 ====================='
                confirm_text += '\nクラスタ: ' + \
                    self.session.get('job_options')['vsphere_cluster']
                confirm_text += '\n仮想マシン: ' + \
                    self.session.get('job_options')['target_vms']
                if str(self.session.get('job_options')['vm_start_stop_enabled']) == 'True':
                    confirm_text += '\n起動/停止: ' + VmStartStop.to_friendly(self.session.get('job_options')['vm_start_stop'])
                    confirm_text += '\nシャットダウン時の最大待ち合わせ時間(秒): ' + str(self.session.get('job_options')['shutdown_timeout_sec'])
                    confirm_text += '\n起動時の最大待ち合わせ時間(秒): ' + str(self.session.get('job_options')['tools_wait_timeout_sec'])
        return confirm_text

    @Logging.func_logger
    def register_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # 次のページへ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="N", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_next,
        )
        # 申請の保存
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="S", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_save,
        )
        # 申請の複製
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="D", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_duplicate,
        )
        # キャンセル
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="X", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=self.on_click_cancel,
        )
        # キャンセル / ESC
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Escape", shift=False, ctrl=False, alt=False, meta=False
            ),
            func=self.on_click_cancel,
        )
        # 共通タブに切り替え
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="G", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=lambda e: self._keyboard_switch_tab(0),
        )
        # 変更対象タブに切り替え
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="T", shift=True, ctrl=True, alt=False, meta=False
            ),
            func=lambda e: self._keyboard_switch_tab(1),
        )

        # 申請の種類に応じて、タブに対応したキーボードショートカットを登録
        db_session = db.get_db()
        request_operation = IaasRequestHelper.get_request(db_session, self.request_id).request_operation
        db_session.close()
        match request_operation:
            case RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY:
                # CPUタブに切り替え
                keyboard_shortcut_manager.register_key_shortcut(
                    key_set=keyboard_shortcut_manager.create_key_set(
                        key="C", shift=True, ctrl=True, alt=False, meta=False
                    ),
                    func=lambda e: self._keyboard_switch_tab(2),
                )
                # メモリタブに切り替え
                keyboard_shortcut_manager.register_key_shortcut(
                    key_set=keyboard_shortcut_manager.create_key_set(
                        key="M", shift=True, ctrl=True, alt=False, meta=False
                    ),
                    func=lambda e: self._keyboard_switch_tab(3),
                )
                # 管理情報タブに切り替え
                keyboard_shortcut_manager.register_key_shortcut(
                    key_set=keyboard_shortcut_manager.create_key_set(
                        key="A", shift=True, ctrl=True, alt=False, meta=False
                    ),
                    func=lambda e: self._keyboard_switch_tab(4),
                )
            case RequestOperation.VM_START_OR_STOP_FRIENDLY:
                # 起動/停止タブに切り替え
                keyboard_shortcut_manager.register_key_shortcut(
                    key_set=keyboard_shortcut_manager.create_key_set(
                        key="B", shift=True, ctrl=True, alt=False, meta=False
                    ),
                    func=lambda e: self._keyboard_switch_tab(2),
                )
                # 管理情報タブに切り替え
                keyboard_shortcut_manager.register_key_shortcut(
                    key_set=keyboard_shortcut_manager.create_key_set(
                        key="A", shift=True, ctrl=True, alt=False, meta=False
                    ),
                    func=lambda e: self._keyboard_switch_tab(3),
                )

        # ログへのセッションダンプ
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="V", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=lambda e, session=self.session: SessionHelper.dump_session(session),
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.register_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False,
            ),
            func=lambda e: keyboard_shortcut_manager.dump_key_shortcuts(),
        )

    @Logging.func_logger
    def _keyboard_switch_tab(self, tab_index):
        self.tabRequest.selected_index = tab_index
        self.tabRequest.update()

    @Logging.func_logger
    def unregister_key_shortcuts(self):
        keyboard_shortcut_manager = KeyboardShortcutManager(self.page)
        # 次のページへ
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="N", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # 申請の保存
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="S", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # 申請の複製
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="D", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # キャンセル
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="X", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # キャンセル / ESC
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Escape", shift=False, ctrl=False, alt=False, meta=False
            ),
        )
        # 共通タブに切り替え
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="G", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # 変更対象タブに切り替え
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="T", shift=True, ctrl=True, alt=False, meta=False
            ),
        )

        # 申請の種類に応じて、タブに対応したキーボードショートカットを登録
        db_session = db.get_db()
        request_operation = IaasRequestHelper.get_request(db_session, self.request_id).request_operation
        db_session.close()
        match request_operation:
            case RequestOperation.VM_CPU_MEMORY_CAHNGE_FRIENDLY:
                # CPUタブに切り替え
                keyboard_shortcut_manager.unregister_key_shortcut(
                    key_set=keyboard_shortcut_manager.create_key_set(
                        key="C", shift=True, ctrl=True, alt=False, meta=False
                    ),
                )
                # メモリタブに切り替え
                keyboard_shortcut_manager.unregister_key_shortcut(
                    key_set=keyboard_shortcut_manager.create_key_set(
                        key="M", shift=True, ctrl=True, alt=False, meta=False
                    ),
                )
            case RequestOperation.VM_START_OR_STOP_FRIENDLY:
                # 起動/停止タブに切り替え
                keyboard_shortcut_manager.unregister_key_shortcut(
                    key_set=keyboard_shortcut_manager.create_key_set(
                        key="B", shift=True, ctrl=True, alt=False, meta=False
                    ),
                )

        # 管理情報タブに切り替え
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="A", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # ログへのセッションダンプ
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="V", shift=True, ctrl=True, alt=False, meta=False
            ),
        )
        # ログへのキーボードショートカット一覧出力
        keyboard_shortcut_manager.unregister_key_shortcut(
            key_set=keyboard_shortcut_manager.create_key_set(
                key="Z", shift=True, ctrl=True, alt=False, meta=False
            ),
        )

    @Logging.func_logger
    def on_click_duplicate(self, e):
        self.click_duplicate_func(e)

    @Logging.func_logger
    def on_click_save(self, e):
        self.click_save_func(e)

    @Logging.func_logger
    def on_click_next(self, e):
        self.session.set('confirm_text', self.generate_confirm_text())
        Logging.info('JOB_OPTIONS: ' + str(self.session.get('job_options')))
        self.step_change_next(e)
