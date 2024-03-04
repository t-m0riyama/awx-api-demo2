import json

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.doc_id_utils import DocIdUtils


class JobExecuteConfirmForm(ft.UserControl):

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
        self.checkShutdownBeforeChange = ft.Checkbox(
            label='設定変更前に、仮想マシンを停止する', value=True)
        self.checkStartupAfterChange = ft.Checkbox(
            label='設定変更後に、仮想マシンを起動する', value=True)
        self.btnNext = ft.ElevatedButton(
            '実行', on_click=self.on_click_send_request)
        self.btnPrev = ft.ElevatedButton(
            '戻る', on_click=self.on_click_previous)
        self.btnCancel = ft.FilledButton(
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

    def generate_job_options(self):
        target_options = [
            'vsphere_cluster',
            'target_vms',
            'vcpus',
            # 'memory_gb',
            # 'reboot_before_change',
            # 'startup_after_change',
        ]
        job_options = {key: str(self.session.get('job_options')[
                                key]) for key in target_options}
        return job_options

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

    def on_click_cancel(self, e):
        self.step_change_cancel(e)

    def on_click_previous(self, e):
        self.step_change_previous(e)

    def on_click_send_request(self, e):
        job_options = self.generate_job_options()

        try:
            self.add_request(job_options, RequestStatus.APPLYING)
        except Exception as ex:
            print('failed to insert record ')
            print(ex)

        job_id = AWXApiHelper.start_job(
            uri_base=self.session.get('awx_url'),
            loginid=self.session.get('awx_loginid'),
            password=self.session.get('awx_password'),
            job_template_name=self.JOB_TEMPLATE_NAME,
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
        db_session.close()
        self.step_change_next(e)
