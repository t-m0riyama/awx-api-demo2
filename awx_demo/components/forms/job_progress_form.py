import flet as ft
from apscheduler.schedulers.background import BackgroundScheduler

from awx_demo.awx_api.awx_api_helper import AWXApiHelper
from awx_demo.components.compounds.form_description import FormDescription
from awx_demo.components.compounds.form_title import FormTitle
from awx_demo.db import db
from awx_demo.db_helper.iaas_request_helper import IaasRequestHelper
from awx_demo.db_helper.types.request_status import RequestStatus


class JobProgressForm(ft.UserControl):

    # const
    CONTENT_HEIGHT = 500
    CONTENT_WIDTH = 700
    BODY_HEIGHT = 250
    JOB_STATUS_CHECK_ID = 'job_status_check'

    def __init__(self, session, request_id, height=CONTENT_HEIGHT, width=CONTENT_WIDTH, body_height=BODY_HEIGHT, step_change_exit=None):
        self.session = session
        self.request_id = request_id
        self.content_height = height
        self.content_width = width
        self.body_height = body_height
        self.step_change_exit = step_change_exit
        super().__init__()

    def build(self):
        formTitle = FormTitle('処理の進捗', 'ジョブの進捗状況', self.content_width)
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

        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(
            self.refresh_progress, 'interval', seconds=3, id=self.JOB_STATUS_CHECK_ID)
        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            pass

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

    def refresh_progress(self):
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
            self.pbJob.value = 1.0
            try:
                self.scheduler.remove_job(self.JOB_STATUS_CHECK_ID)
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
            IaasRequestHelper.update_request_status(db.get_db(), self.session.get(
                'document_id'), RequestStatus.COMPLETED, self.session)
        elif job_status == AWXApiHelper.JOB_STATUS_FAILED:
            try:
                self.scheduler.remove_job(self.JOB_STATUS_CHECK_ID)
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

        if job_status == AWXApiHelper.JOB_STATUS_RUNNING:
            if self.pbJob.value < 0.9:
                self.pbJob.value += 0.1
        self.pbJob.update()

    def exit_clicked(self, e):
        self.step_change_exit(e)
