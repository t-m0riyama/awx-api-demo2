import json

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.types.user_role import UserRole
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.doc_id_utils import DocIdUtils
from awx_demo.utils.logging import Logging


class SendRequestConfirmForm(ft.UserControl):

    # const
    CONTENT_HEIGHT = 600
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 300
    DEFAULT_FORM_TITLE = '確認'
    JOB_TEMPLATE_NAME = 'vm-config-utils_set_vm_cpu'
    VARS_TEMPLATE_NAME = 'aap_demo_extra_vars'
    DUCUMENT_ID_LENGTH = 7

    def __init__(self, session, title=DEFAULT_FORM_TITLE, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.title = title
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel
        super().__init__()

    def build(self):
        formTitle = FormTitle(self.title, '変更内容の確認', self.content_width)
        formDescription = FormDescription('以下の内容で、変更を適用します。')
        self.tfConfirmText = ft.TextField(
            value=self.session.get('confirm_text'),
            color=ft.colors.PRIMARY,
            multiline=True,
            max_lines=4,
            read_only=True,
        )
        execute_disabled = True if self.session.get(
            'user_role') == UserRole.USER_ROLE else False
        self.checkShutdownBeforeChange = ft.Checkbox(
            label='設定変更前に、仮想マシンを停止する',
            value=self.session.get('job_options')['shutdown_before_change'] if 'shutdown_before_change' in self.session.get('job_options') else True,
        )
        self.checkStartupAfterChange = ft.Checkbox(
            label='設定変更後に、仮想マシンを起動する',
            value=self.session.get('job_options')['startup_after_change'] if 'startup_after_change' in self.session.get('job_options') else True,
        )
        self.checkExecuteJobImmediately = ft.Checkbox(
            label='この変更作業をすぐに実行する', value=False, disabled=execute_disabled)
        self.btnNext = ft.FilledButton(
            '申請する', on_click=self.on_click_send_request)
        self.btnPrev = ft.ElevatedButton(
            '戻る', on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            'キャンセル', on_click=self.on_click_cancel)

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
                self.tfConfirmText,
                self.checkShutdownBeforeChange,
                self.checkStartupAfterChange,
                self.checkExecuteJobImmediately,
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

        return ft.Card(
            ft.Container(
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
            ),
        )

    @Logging.func_logger
    def generate_job_options(self):
        target_options = [
            'vsphere_cluster',
            'target_vms',
            'vcpus',
            'memory_gb',
            'change_vm_cpu_enabled',
            'change_vm_memory_enabled',
            'shutdown_before_change',
            'startup_after_change',
        ]
        job_options = {key: str(self.session.get('job_options')[key]) for key in target_options}
        return job_options

    @Logging.func_logger
    def add_request(self, job_options, request_status):
        document_id = DocIdUtils.generate_id(self.DUCUMENT_ID_LENGTH)
        self.session.set('document_id', document_id)
        db_session = db.get_db()
        IaasRequestHelper.add_request(
            db_session=db_session,
            request_id=self.session.get('document_id'),
            request_deadline=self.session.get('request_deadline'),
            request_user=self.session.get('awx_loginid'),
            request_category=self.session.get('request_category'),
            request_operation=self.session.get('request_operation'),
            request_text=self.session.get('request_text'),
            job_options=json.dumps(job_options),
            request_status=request_status,
            session=self.session,
        )
        db_session.close()

    @Logging.func_logger
    def on_click_cancel(self, e):
        self.step_change_cancel(e)

    @Logging.func_logger
    def on_click_previous(self, e):
        self.step_change_previous(e)

    @Logging.func_logger
    def on_click_send_request(self, e):
        self.session.get('job_options')['shutdown_before_change'] = self.checkShutdownBeforeChange.value
        self.session.get('job_options')['startup_after_change'] = self.checkStartupAfterChange.value
        job_options = self.generate_job_options()

        if self.checkExecuteJobImmediately.value:
            self.session.set('execute_job_immediately', True)

            try:
                self.add_request(job_options, RequestStatus.APPLYING)
            except Exception as ex:
                Logging.error('failed to insert record ')
                Logging.error(ex)
            
            db_session = db.get_db()
            request = IaasRequestHelper.get_request(db_session, self.session.get('document_id'))
            job_id = AWXApiHelper.start_job(
                uri_base=self.session.get('awx_url'),
                loginid=self.session.get('awx_loginid'),
                password=self.session.get('awx_password'),
                job_template_name=self.JOB_TEMPLATE_NAME,
                request=request,
                job_options=job_options,
                session=self.session,
            )

            db_session = db.get_db()
            IaasRequestHelper.update_request_iaas_user(db_session, self.session.get(
                'document_id'), self.session.get('awx_loginid'), self.session)
            if job_id > 0:
                self.session.set('job_id', job_id)
                IaasRequestHelper.update_job_id(
                    db_session, self.session.get('document_id'), job_id)
            else:
                pass
        else:
            try:
                self.add_request(job_options, RequestStatus.START)
            except Exception as ex:
                Logging.error('failed to insert record ')
                Logging.error(ex)

        self.step_change_next(e)
