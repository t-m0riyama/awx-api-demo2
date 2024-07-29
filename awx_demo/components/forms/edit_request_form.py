import flet as ft

from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.forms.edit_tab.manage_info_tab_form import ManageInfoTabForm
from awx_demo.components.forms.edit_tab.request_common_info_tab_form import RequestCommonInfoTabForm
from awx_demo.components.forms.edit_tab.select_target_tab_form import SelectTargetTabForm
from awx_demo.components.forms.edit_tab.set_vm_cpu_tab_form import SetVmCpuTabForm
from awx_demo.components.forms.edit_tab.set_vm_memory_tab_form import SetVmMemoryTabForm
from awx_demo.components.session_helper import SessionHelper
from awx_demo.components.types.user_role import UserRole
from awx_demo.db import db
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class EditRequestForm(ft.Card):

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
        self.click_execute_func = click_execute_func
        self.click_duplicate_func = click_duplicate_func
        self.click_save_func = click_save_func
        self.click_cancel_func = click_cancel_func

        self.tab_content_height = self.content_height - 80
        self.tab_content_width = self.content_width
        self.tab_body_height = self.body_height - 80

        db_session = db.get_db()
        SessionHelper.load_request_to_session_from_db(
            self.session, db_session, self.request_id)
        db_session.close()

        # overlayを利用する可能性があるコントロールは、あらかじめインスタンスを作成する
        self.formCreateRequest = RequestCommonInfoTabForm(
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

        # controls
        if self.session.get('user_role') == UserRole.USER_ROLE:
            formTitle = FormTitle('申請の詳細', '', self.content_width)
        else:
            formTitle = FormTitle('申請の編集', '', self.content_width)

        self.tabRequest = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text='共通',
                    content=self.formCreateRequest,
                ),
                ft.Tab(
                    text='変更対象',
                    content=self.formSelectTarget,
                ),
                ft.Tab(
                    text='CPU',
                    content=self.formSetVmCpu,
                ),
                ft.Tab(
                    text='メモリ',
                    content=self.formSetVmMemory,
                ),
                ft.Tab(
                    text='管理情報',
                    content=self.formManageInfo,
                ),
            ],
            scrollable=True,
            expand=1,
        )
        change_disabled = True if self.session.get(
            'user_role') == UserRole.USER_ROLE else False
        is_execute_disabled = self.session.get('request_status') not in [
            RequestStatus.APPROVED, RequestStatus.COMPLETED]
        self.btnExecute = ft.ElevatedButton(
            '実行', on_click=self.on_click_execute, disabled=(is_execute_disabled or change_disabled))
        self.btnSave = ft.ElevatedButton(
            '保存', on_click=self.on_click_save, disabled=change_disabled)
        self.btnDuplicate = ft.ElevatedButton(
            '複製', on_click=self.on_click_duplicate, disabled=change_disabled)
        self.btnCancel = ft.FilledButton(
            '閉じる', on_click=self.on_click_cancel)

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

        controls = ft.Container(
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
        super().__init__(controls)

    @Logging.func_logger
    def generate_confirm_text(self):
        confirm_text = '== 基本情報 ====================='
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
        return confirm_text

    @Logging.func_logger
    def on_click_cancel(self, e):
        self.click_cancel_func(e)

    @Logging.func_logger
    def on_click_duplicate(self, e):
        self.click_duplicate_func(e)

    @Logging.func_logger
    def on_click_save(self, e):
        self.click_save_func(e)

    @Logging.func_logger
    def on_click_execute(self, e):
        self.session.set('confirm_text', self.generate_confirm_text())
        Logging.info('JOB_OPTIONS: ' + str(self.session.get('job_options')))
        self.click_execute_func(e)
