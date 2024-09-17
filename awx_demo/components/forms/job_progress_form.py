import os
from datetime import datetime, timedelta

import flet as ft
from apscheduler.schedulers.background import BackgroundScheduler

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class JobProgressForm(ft.Card):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    JOB_STATUS_CHECK_ID_PREFIX = 'job_status_check'
    JOB_STATUS_CHECK_TIMEOUT_SECS_DEFAULT=3600
    JOB_STATUS_CHECK_INTERVAL_SECS_DEFAULT=3

    def __init__(self, session, request_id, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_exit=None):
        self.session = session
        self.request_id = request_id
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_exit = step_change_exit
        self.scheduler_job_id = ''

        # controls
        formTitle = FormTitle('処理の進捗', 'ジョブの進捗状況')
        formDescription = FormDescription('ジョブの進捗状況を表示します。')
        self.pbJob = ft.ProgressBar(value=0, width=self.CONTENT_WIDTH)
        self.lvProgressLog = ft.ListView(
            # expand=1,
            spacing=10,
            padding=10,
            divider_thickness=1,
            auto_scroll=True)
        self.lvProgressLog.controls.append(
            ft.Row(
                [
                    ft.Icon(ft.icons.INFO_OUTLINED, color=ft.colors.BLUE_500),
                    ft.Text(
                        value='処理を開始しました。',
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        color=ft.colors.SECONDARY
                    ),
                ]
            )
        )
        self.btnExit = ft.FilledButton(
            '閉じる', on_click=self.exit_clicked, disabled=True)

        # Content
        header = ft.Container(
            formTitle,
            margin=ft.margin.only(bottom=20),
        )
        body = ft.Column(
            [
                formDescription,
                self.pbJob,
                self.lvProgressLog,
            ],
            height=self.body_height,
        )
        footer = ft.Row(
            [
                self.btnExit,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.scheduler_job_id = f'{self.JOB_STATUS_CHECK_ID_PREFIX}_{self.session.get("job_id")}'
        check_timeout = int(os.getenv('RMX_JOB_STATUS_CHECK_TIMEOUT_SECS', self.JOB_STATUS_CHECK_TIMEOUT_SECS_DEFAULT))
        check_internal = int(os.getenv('RMX_JOB_STATUS_CHECK_INTERVAL_SECS', self.JOB_STATUS_CHECK_INTERVAL_SECS_DEFAULT))

        # ジョブがタイムアウトし、終了する時間を求める
        dt_now = datetime.now()
        dt_delta = timedelta(seconds=check_timeout)
        job_end_date = (dt_now + dt_delta).strftime('%Y-%m-%d %H:%M:%S')
        Logging.info(f'JOB_TIMEOUT_DATE({self.scheduler_job_id}): {job_end_date}')

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.refresh_progress, 'interval', seconds=check_internal, end_date=job_end_date, id=self.scheduler_job_id)
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

        controls = ft.Container(
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
        super().__init__(controls)

    @Logging.func_logger
    def refresh_progress(self):
        if self.session.get('job_id') is None:
            self._on_job_request_failed()
            return

        db_session = db.get_db()
        request = IaasRequestHelper.get_request(db_session, self.request_id)
        job_status = AWXApiHelper.get_job_status(
            uri_base=self.session.get('awx_url'),
            loginid=self.session.get('awx_loginid'),
            password=self.session.get('awx_password'),
            request=request,
            job_id=self.session.get('job_id'),
            session=self.session,
        )
        db_session.close()
        if job_status == AWXApiHelper.JOB_STATUS_SUCCEEDED:
            self._on_job_status_completed()
            IaasRequestHelper.update_request_status(db.get_db(), self.session.get(
                'document_id'), RequestStatus.COMPLETED, self.session)
        elif job_status == AWXApiHelper.JOB_STATUS_FAILED:
            self._on_job_status_request_failed()

        if job_status == AWXApiHelper.JOB_STATUS_RUNNING:
            if self.pbJob.value < 0.9:
                self.pbJob.value += 0.1
        self.pbJob.update()

    @Logging.func_logger
    def _on_job_status_completed(self):
        self.pbJob.value = 1.0
        try:
            self.scheduler.remove_job(self.scheduler_job_id)
            self.scheduler.pause()
        except (KeyboardInterrupt, SystemExit):
            pass

        self.lvProgressLog.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.icons.THUMB_UP_OUTLINED,
                                color=ft.colors.BLUE_500),
                        ft.Text(
                            value='処理は正常終了しました。',
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.colors.SECONDARY
                        ),
                    ]
                )
            )
        self.lvProgressLog.controls.append(
                ft.TextButton(
                    'ジョブ出力の参照: ' +
                    self.session.get(
                        'awx_url') + '/#/jobs/playbook/{}/output'.format(self.session.get('job_id')),
                    url=self.session.get(
                        'awx_url') + '/#/jobs/playbook/{}/output'.format(self.session.get('job_id')),
                ),
            )
        self.btnExit.disabled = False
        self.lvProgressLog.update()
        self.btnExit.update()

    @Logging.func_logger
    def _on_job_status_request_failed(self):
        try:
            self.scheduler.remove_job(self.scheduler_job_id)
            self.scheduler.pause()
        except (KeyboardInterrupt, SystemExit):
            pass
        self.lvProgressLog.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.icons.ERROR_OUTLINED,
                                color=ft.colors.ERROR),
                        ft.Text(
                            value='処理に失敗しました。',
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.colors.SECONDARY
                        ),
                    ]
                )
            )
        self.lvProgressLog.controls.append(
                ft.TextButton(
                    'ジョブ出力の参照: ' +
                    self.session.get(
                        'awx_url') + '/#/jobs/playbook/{}/output'.format(self.session.get('job_id')),
                    url=self.session.get(
                        'awx_url') + '/#/jobs/playbook/{}/output'.format(self.session.get('job_id')),
                ),
            )
        self.btnExit.disabled = False
        self.lvProgressLog.update()
        self.btnExit.update()

    @Logging.func_logger
    def _on_job_request_failed(self):
        self.lvProgressLog.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.icons.ERROR_OUTLINED,
                                color=ft.colors.ERROR),
                        ft.Text(
                            value='ジョブの実行要求に失敗しました。',
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.colors.SECONDARY
                        ),
                    ]
                )
            )

        try:
            self.scheduler.remove_job(self.scheduler_job_id)
            self.scheduler.pause()
        except (KeyboardInterrupt, SystemExit):
            pass
        self.btnExit.disabled = False
        self.lvProgressLog.update()
        self.btnExit.update()

    @Logging.func_logger
    def exit_clicked(self, e):
        self.step_change_exit(e)
