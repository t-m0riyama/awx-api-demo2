import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import flet as ft
from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.background import BackgroundScheduler

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.components.wizards.base_wizard_card import BaseWizardCard
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.logging import Logging


class JobProgressForm(BaseWizardCard):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    JOB_STATUS_CHECK_ID_PREFIX = 'job_status_check'
    JOB_STATUS_CHECK_TIMEOUT_SECS_DEFAULT = 3600
    JOB_STATUS_CHECK_INTERVAL_SECS_DEFAULT = 5
    JOB_STATUS_CHECK_RESULT_NEXT_RUNNABLE = 0
    JOB_STATUS_CHECK_RESULT_NEXT_NOT_RUNNABLE = 1
    JOB_STATUS_CHECK_RESULT_EXECUTABLE_TIMEOUT = 2

    def __init__(self, session, page: ft.Page, request_id, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_exit=None):
        self.session = session
        self.page = page
        self.request_id = request_id
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_cancel = step_change_exit
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
                    ft.Icon(ft.Icons.INFO_OUTLINED, color=ft.Colors.BLUE_500),
                    ft.Text(
                        value=f'{JobProgressForm._get_timestamp()} 処理を開始しました。',
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        color=ft.Colors.SECONDARY
                    ),
                ]
            )
        )
        self.btnExit = ft.FilledButton(
            '閉じる', tooltip='閉じる (Cotrol+Shift+X)', on_click=self.on_click_cancel, disabled=True)

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
        self.check_timeout = int(os.getenv('RMX_JOB_STATUS_CHECK_TIMEOUT_SECS', self.JOB_STATUS_CHECK_TIMEOUT_SECS_DEFAULT))
        self.check_interval = int(os.getenv('RMX_JOB_STATUS_CHECK_INTERVAL_SECS', self.JOB_STATUS_CHECK_INTERVAL_SECS_DEFAULT))

        # ジョブがタイムアウトし、終了する時間を求める
        dt_now = datetime.now()
        dt_delta = timedelta(seconds=self.check_timeout)
        self.job_end_date = dt_now + dt_delta
        job_end_date_str = self.job_end_date.strftime('%Y-%m-%d %H:%M:%S')
        Logging.info(f'JOB_TIMEOUT_DATE({self.scheduler_job_id}): {job_end_date_str}')

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.refresh_progress, 'interval', seconds=self.check_interval, end_date=job_end_date_str, id=self.scheduler_job_id)
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

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
    def refresh_progress(self):
        if self.session.get('job_id') is None:
            self._on_job_request_failed()
            IaasRequestHelper.update_request_status(
                db_session=db.get_db(),
                session=self.session,
                request_id=self.session.get('document_id'),
                request_status=RequestStatus.APPLYING_FAILED,
            )
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
            IaasRequestHelper.update_request_status(
                db_session=db.get_db(),
                session=self.session,
                request_id=self.session.get('document_id'),
                request_status=RequestStatus.COMPLETED,
            )
            self.pbJob.update()
            return
        elif job_status == AWXApiHelper.JOB_STATUS_RUNNING:
            if self.pbJob.value < 0.9:
                self.pbJob.value += 0.1
            self.pbJob.update()
        elif job_status == AWXApiHelper.JOB_STATUS_FAILED:
            self._on_job_status_request_failed()
            IaasRequestHelper.update_request_status(
                db_session=db.get_db(),
                session=self.session,
                request_id=self.session.get('document_id'),
                request_status=RequestStatus.APPLYING_FAILED,
            )
            self.pbJob.update()
            return

        # ジョブの進捗状況の次回の確認が可能かどうかを判定
        next_runnable = self._job_next_runnable()
        if next_runnable == self.JOB_STATUS_CHECK_RESULT_NEXT_RUNNABLE:
            return
        elif next_runnable == self.JOB_STATUS_CHECK_RESULT_NEXT_NOT_RUNNABLE:
            self._on_job_execution_failed()
            return
        elif next_runnable == self.JOB_STATUS_CHECK_RESULT_EXECUTABLE_TIMEOUT:
            self._on_job_status_timeout()
            return

    @Logging.func_logger
    def _job_next_runnable(self):
        jst = ZoneInfo("Asia/Tokyo")
        job = self.scheduler.get_job(self.scheduler_job_id)
        if "next_run_time" not in dir(job):
            return self.JOB_STATUS_CHECK_RESULT_NEXT_NOT_RUNNABLE

        dt_next_check = job.next_run_time.replace(tzinfo=jst)
        dt_end_time = self.job_end_date.replace(tzinfo=jst)
        diff_date = (dt_end_time - dt_next_check).seconds - float(self.check_interval)

        if diff_date > 0:
            Logging.info(f"JOB_NEXT_RUN / TIMEOUT / DIFF: {dt_next_check.strftime('%Y-%m-%d %H:%M:%S')} / {dt_end_time.strftime('%Y-%m-%d %H:%M:%S')} / {diff_date}")
            return self.JOB_STATUS_CHECK_RESULT_NEXT_RUNNABLE
        else:
            Logging.warning(f"JOB_NEXT_RUN / TIMEOUT / DIFF: {dt_next_check.strftime('%Y-%m-%d %H:%M:%S')} / {dt_end_time.strftime('%Y-%m-%d %H:%M:%S')} / {diff_date}")
            return self.JOB_STATUS_CHECK_RESULT_EXECUTABLE_TIMEOUT

    @Logging.func_logger
    def _on_job_status_completed(self):
        self.pbJob.value = 1.0
        job_succeeded = self._stop_job_and_scheduler()

        if job_succeeded:
            self.lvProgressLog.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.THUMB_UP_OUTLINED,
                                color=ft.Colors.BLUE_500),
                        ft.Text(
                            value=f'{JobProgressForm._get_timestamp()} 処理は正常終了しました。',
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.Colors.SECONDARY
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
        else:
            self.lvProgressLog.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.ERROR_OUTLINED,
                                color=ft.Colors.ERROR),
                        ft.Text(
                            value=f'{JobProgressForm._get_timestamp()} 処理は異常終了しました。実行可能な時間を超過した可能性があります。',
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.Colors.SECONDARY
                        ),
                    ]
                )
            )
        self.btnExit.disabled = False
        self.lvProgressLog.update()
        self.btnExit.update()

    @Logging.func_logger
    def _on_job_status_timeout(self):
        self._stop_job_and_scheduler()
        self.lvProgressLog.controls.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.ERROR_OUTLINED,
                            color=ft.Colors.ERROR),
                    ft.Text(
                        value=f'{JobProgressForm._get_timestamp()} ジョブの実行可能時間を超過しました。',
                        theme_style=ft.TextThemeStyle.BODY_LARGE,
                        color=ft.Colors.SECONDARY
                    ),
                ]
            )
        )
        self.btnExit.disabled = False
        self.lvProgressLog.update()
        self.btnExit.update()

    @Logging.func_logger
    def _on_job_status_request_failed(self):
        self._stop_job_and_scheduler()
        self.lvProgressLog.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.ERROR_OUTLINED,
                                color=ft.Colors.ERROR),
                        ft.Text(
                            value=f'{JobProgressForm._get_timestamp()} 処理に失敗しました。',
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.Colors.SECONDARY
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
                        ft.Icon(ft.Icons.ERROR_OUTLINED,
                                color=ft.Colors.ERROR),
                        ft.Text(
                            value=f'{JobProgressForm._get_timestamp()} ジョブの実行要求に失敗しました。',
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.Colors.SECONDARY
                        ),
                    ]
                )
            )

        self._stop_job_and_scheduler()
        self.btnExit.disabled = False
        self.lvProgressLog.update()
        self.btnExit.update()

    @Logging.func_logger
    def _on_job_execution_failed(self):
        self.lvProgressLog.controls.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.ERROR_OUTLINED,
                                color=ft.Colors.ERROR),
                        ft.Text(
                            value=f'{JobProgressForm._get_timestamp()} ジョブの実行中にエラーが発生しました。',
                            theme_style=ft.TextThemeStyle.BODY_LARGE,
                            color=ft.Colors.SECONDARY
                        ),
                    ]
                )
            )

        self._stop_job_and_scheduler()
        self.btnExit.disabled = False
        self.lvProgressLog.update()
        self.btnExit.update()

    @Logging.func_logger
    def _stop_job_and_scheduler(self):
        job_succeeded = True
        try:
            self.scheduler.remove_job(self.scheduler_job_id)
            self.scheduler.pause()
        except JobLookupError:
            job_succeeded = False
            self.scheduler.pause()
            Logging.warning(f'JOB_AND_SCHEDULER_STOP: ビルトインスケジューラのジョブID({self.scheduler_job_id}) が見つかりません。実行可能な時間を超過した可能性があります。')
        except (KeyboardInterrupt, SystemExit):
            pass
        return job_succeeded

    @staticmethod
    @Logging.func_logger
    def _get_timestamp():
        dt_now = datetime.now()
        timestamp = dt_now.strftime('%Y-%m-%d %H:%M:%S')
        return timestamp
