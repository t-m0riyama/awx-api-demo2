import json
from distutils.util import strtobool

import flet as ft

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.awx_api.job_options_helper import JobOptionsHelper
from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.types.user_role import UserRole
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_category import RequestOperation
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.doc_id_utils import DocIdUtils
from awx_demo.utils.logging import Logging


class SendRequestConfirmForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 600
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 300
    DEFAULT_FORM_TITLE = '確認'
    DOCUMENT_ID_LENGTH = 7

    def __init__(self, session, page: ft.Page, title=DEFAULT_FORM_TITLE, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_next=None, step_change_previous=None, step_change_cancel=None):
        self.session = session
        self.page = page
        self.title = title
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_next = step_change_next
        self.step_change_previous = step_change_previous
        self.step_change_cancel = step_change_cancel

        # controls
        formTitle = FormTitle(self.title, '変更内容の確認')
        formDescription = FormDescription('以下の内容で、変更を適用します。')
        self.tfConfirmText = ft.TextField(
            value=self.session.get('confirm_text'),
            color=ft.Colors.PRIMARY,
            multiline=True,
            max_lines=4,
            read_only=True,
        )
        execute_disabled = True if self.session.get('user_role') == UserRole.USER_ROLE else False
        self.checkShutdownBeforeChange = ft.Checkbox(
            label='設定変更前に、仮想マシンを停止する',
            value=bool(strtobool(str(self.session.get('job_options')['shutdown_before_change']))) if 'shutdown_before_change' in self.session.get('job_options') else True,
            autofocus=True,
            on_change=self.on_change_shutdown_before_change,
        )
        self.checkStartupAfterChange = ft.Checkbox(
            label='設定変更後に、仮想マシンを起動する',
            value=bool(strtobool(str(self.session.get('job_options')['startup_after_change']))) if 'startup_after_change' in self.session.get('job_options') else True,
            autofocus=True,
            on_change=self.on_change_startup_after_change,
        )
        self.checkExecuteJobImmediately = ft.Checkbox(
            label='この変更作業をすぐに実行する', value=False, disabled=execute_disabled)
        self.btnNext = ft.FilledButton(
            '申請する', tooltip='申請する (Cotrol+Shift+N)', on_click=self.on_click_next)
        self.btnPrev = ft.ElevatedButton(
            '戻る', tooltip='戻る (Cotrol+Shift+P)', on_click=self.on_click_previous)
        self.btnCancel = ft.ElevatedButton(
            'キャンセル', tooltip='キャンセル (Cotrol+Shift+X)', on_click=self.on_click_cancel)

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body_general = ft.Column(
            [
                formDescription,
                self.tfConfirmText,
                self.checkShutdownBeforeChange,
                self.checkStartupAfterChange,
                self.checkExecuteJobImmediately,
            ],
            height=self.body_height,
        )
        body_start_stop = ft.Column(
            [
                formDescription,
                self.tfConfirmText,
                self.checkExecuteJobImmediately,
            ],
            height=self.body_height,
        )
        body = body_start_stop if self.session.get('request_operation') == RequestOperation.VM_START_OR_STOP_FRIENDLY else body_general
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
    def _add_request(self, job_options, request_status):
        document_id = DocIdUtils.generate_id(self.DOCUMENT_ID_LENGTH)
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
    def on_click_next(self, e):
        self._lock_form_controls()

        if not self.session.get('request_operation') == RequestOperation.VM_START_OR_STOP_FRIENDLY:
            self.session.get('job_options')['shutdown_before_change'] = str(self.checkShutdownBeforeChange.value)
            self.session.get('job_options')['startup_after_change'] = str(self.checkStartupAfterChange.value)
        job_options = JobOptionsHelper.generate_job_options(self.session, RequestOperation.to_formal(self.session.get('request_operation')))

        if self.checkExecuteJobImmediately.value:
            self.session.set('execute_job_immediately', True)

            try:
                self._add_request(job_options, RequestStatus.APPLYING)
            except Exception as ex:
                Logging.error('failed to insert record ')
                Logging.error(ex)

            db_session = db.get_db()
            request = IaasRequestHelper.get_request(db_session, self.session.get('document_id'))
            job_template_name = JobOptionsHelper.get_job_template_name(RequestOperation.to_formal(self.session.get('request_operation')))
            job_id = AWXApiHelper.start_job(
                uri_base=self.session.get('awx_url'),
                loginid=self.session.get('awx_loginid'),
                password=self.session.get('awx_password'),
                job_template_name=job_template_name,
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
            db_session.close()
        else:
            try:
                self._add_request(job_options, RequestStatus.START)
            except Exception as ex:
                Logging.error('failed to insert record ')
                Logging.error(ex)

        self._unlock_form_controls()
        self.step_change_next(e)

    @Logging.func_logger
    def on_change_shutdown_before_change(self, e):
        self.session.get('job_options')['shutdown_before_change'] = str(self.checkShutdownBeforeChange.value)

    @Logging.func_logger
    def on_change_startup_after_change(self, e):
        self.session.get('job_options')['startup_after_change'] = str(self.checkStartupAfterChange.value)
