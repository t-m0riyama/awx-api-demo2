import datetime
import json

import jmespath
import requests
from requests.auth import HTTPBasicAuth

from awx_demo.db import db
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.db_helper.iaas_request_report_helper import IaasRequestReportHelper
from awx_demo.notification.notification_spec import NotificationMethod, NotificationSpec
from awx_demo.notification.notificator import Notificator
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.event_manager import EventManager
from awx_demo.utils.logging import Logging


class AWXApiHelper:

    # const
    JOB_STATUS_SUCCEEDED = 'successful'
    JOB_STATUS_FAILED = 'failed'
    JOB_STATUS_RUNNING = 'running'
    JOB_TEMPLATE_ID_NOT_FOUND = -1
    JOB_TEMPLATE_ID_CONNECTION_FAILED = -2
    JOB_LAUNCH_FAILED = -3
    JOB_LAUNCH_CONNECTION_FAILED = -4
    JOB_STATUS_CONNECTION_FAILED = -5

    @staticmethod
    def login(uri_base, loginid, password):
        reqest_url = uri_base + '/api/v2/me/'
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.get(reqest_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=False)
            Logging.info('login_url: ' + reqest_url)
            Logging.info('login_status: ' + str(response.status_code))
            if response.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            Logging.error(e)
            return False

    @staticmethod
    def get_teams_user_belong(uri_base, loginid, password):
        reqest_url = uri_base + '/api/v2/me/'
        headers = {'Content-Type': 'application/json'}
        try:
            response_me = requests.get(reqest_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=False)
            if response_me.status_code != 200:
                Logging.error("Failed to retrieve information for user")
                return False

            Logging.info("awx_teams_url" +
                  jmespath.search("results[0].related.teams", response_me.json()))
            teams_url = uri_base + \
                jmespath.search("results[0].related.teams", response_me.json())
            response_teams = requests.get(
                teams_url, headers=headers, auth=HTTPBasicAuth(loginid, password), verify=False)
            if response_teams.status_code != 200:
                Logging.error("Failed to retrieve information for teams")
                return False

            teams = []
            for team_name in jmespath.search("results[].name", response_teams.json()):
                teams.append(team_name)
            return teams
        except Exception as e:
            Logging.error(e)
            return None

    @staticmethod
    def get_users(uri_base, loginid, password):
        reqest_url = uri_base + '/api/v2/users/'
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.get(reqest_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=False)
            if response.status_code == 200:
                return jmespath.search('results', response.json())
            else:
                return None
        except Exception as e:
            Logging.error(e)
            return None

    @staticmethod
    def start_job(uri_base, loginid, password, job_template_name, request, job_options, session):
        headers = {'Content-Type': 'application/json'}
        vars_json = AWXApiHelper.generate_vars(job_options)
        try:
            job_template_id = AWXApiHelper.get_job_template_id(
                uri_base, loginid, password, job_template_name)
            launch_url = uri_base + \
                '/api/v2/job_templates/{}/launch/'.format(job_template_id)
            # ジョブテンプレートが見つからない場合は、エラー終了
            if job_template_id == AWXApiHelper.JOB_TEMPLATE_ID_NOT_FOUND:
                Logging.error('TEMPLATE NOT FOUND: ' + job_template_name)
                return AWXApiHelper.JOB_LAUNCH_FAILE
            
            Logging.info('launch_url: ' + launch_url)
            Logging.info('vars: ' + vars_json)
            detail = IaasRequestReportHelper.generate_request_detail(request)
            response = requests.post(launch_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=False, data=vars_json)
            if response.status_code == 201:
                response_results = jmespath.search('job', response.json())
                Logging.info('job_id: ' + str(response_results))
                AWXApiHelper._emit_event_on_start_job(
                    db_session=db.get_db(),
                    user=session.get('awx_loginid'),
                    request_id=session.get('request_id'),
                    request_category=request.request_category,
                    request_operation=request.request_operation,
                    request_text=request.request_text,
                    request_deadline=request.request_deadline,
                    detail=detail,
                    is_succeeded=True,
                )
                return response_results
            else:
                AWXApiHelper._emit_event_on_start_job(
                    db_session=db.get_db(),
                    user=session.get('awx_loginid'),
                    request_id=session.get('request_id'),
                    request_category=request.request_category,
                    request_operation=request.request_operation,
                    request_text=request.request_text,
                    request_deadline=request.request_deadline,
                    detail=detail,
                    is_succeeded=False,
                )
                Logging.error('status: {}'.format(response.status_code))
                Logging.error('response: {}'.format(response.text))
                return AWXApiHelper.JOB_LAUNCH_FAILED
        except Exception as e:
            return AWXApiHelper.JOB_LAUNCH_CONNECTION_FAILED

    @staticmethod
    def generate_vars(job_options):
        return json.dumps({"extra_vars": job_options})

    @staticmethod
    def get_job_template_id(uri_base, loginid, password, job_template_name):
        job_templates_url = uri_base + '/api/v2/job_templates/{}/'.format(job_template_name)
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.get(job_templates_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=False)
            if response.status_code == 200:
                return (response.json())['id']
            else:
                return AWXApiHelper.JOB_TEMPLATE_ID_NOT_FOUND
        except Exception as e:
            Logging.error(e)
            Logging.error('job_template_url: ' + job_templates_url)
            return AWXApiHelper.JOB_TEMPLATE_ID_CONNECTION_FAILED

    @staticmethod
    def get_job_status(uri_base, loginid, password, request, job_id, session):
        job_status_url = uri_base + '/api/v2/jobs/{}/'.format(job_id)
        headers = {'Content-Type': 'application/json'}
        Logging.info('job_status_url: ' + job_status_url)
        detail = IaasRequestReportHelper.generate_request_detail(request)
        try:
            response = requests.get(job_status_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=False)
            Logging.info('job_status_status_code: ' + str(response.status_code))
            if response.status_code == 200:
                job_status = jmespath.search('status', response.json())
                job_status_succeed = True if job_status == AWXApiHelper.JOB_STATUS_SUCCEEDED else False
                Logging.info("job_status: " + str(job_status))
                if job_status == AWXApiHelper.JOB_STATUS_SUCCEEDED or job_status == AWXApiHelper.JOB_STATUS_FAILED:
                    AWXApiHelper._emit_event_on_job_completed(
                        db_session=db.get_db(),
                        user=session.get('awx_loginid'),
                        request_id=session.get('request_id'),
                        request_category=request.request_category,
                        request_operation=request.request_operation,
                        request_text=request.request_text,
                        request_deadline=request.request_deadline,
                        detail=detail,
                        is_succeeded=job_status_succeed,
                    )
                return job_status
            else:
                AWXApiHelper._emit_event_on_job_completed(
                    db_session=db.get_db(),
                    user=session.get('awx_loginid'),
                    request_id=session.get('request_id'),
                    request_category=request.request_category,
                    request_operation=request.request_operation,
                    request_text=request.request_text,
                    request_deadline=request.request_deadline,
                    detail=detail,
                    is_succeeded=False,
                )
                return str(AWXApiHelper.JOB_STATUS_FAILED)
        except Exception as e:
            Logging.error(e)
            AWXApiHelper._emit_event_on_job_completed(
                db_session=db.get_db(),
                user=session.get('awx_loginid'),
                request_id=session.get('request_id'),
                request_category=request.request_category,
                request_operation=request.request_operation,
                request_text=request.request_text,
                request_deadline=request.request_deadline,
                detail=detail,
                is_succeeded=False,
            )
            return str(AWXApiHelper.JOB_STATUS_CONNECTION_FAILED)

    @staticmethod
    def _emit_event(db_session, notification_method: NotificationMethod, title, sub_title, sub_title2, user, request_id, event_type, status, summary, detail='', request_text=None, request_deadline=None, icon=None):
        activity_spec = ActivityHelper.ActivitySpec(
            db_session=db_session,
            user=user,
            request_id=request_id,
            event_type=event_type,
            status=status,
            summary=summary,
            detail=detail,
        )

        notification_specs = []
        # Teams通知を指定された場合
        if notification_method == NotificationMethod.NOTIFY_TEMAS_ONLY or notification_method == NotificationMethod.NOTIFY_TEMAS_AND_MAIL:
            notification_specs.append(
                NotificationSpec(
                    notification_type=Notificator.TEAMS_NOTIFICATION,
                    title=title,
                    sub_title=sub_title,
                    sub_title2=sub_title2,
                    user=user,
                    request_id=request_id,
                    event_type=event_type,
                    status=status,
                    summary=summary,
                    detail=detail,
                    request_text=request_text,
                    request_deadline=request_deadline,
                    icon=icon,
                )
            )
        # メール通知を指定された場合
        if notification_method == NotificationMethod.NOTIFY_MAIL_ONLY or notification_method == NotificationMethod.NOTIFY_TEMAS_AND_MAIL:
            notification_specs.append(
                NotificationSpec(
                    notification_type=Notificator.MAIL_NOTIFICATION,
                    title=summary,
                    sub_title="",
                    sub_title2="",
                    user=user,
                    request_id=request_id,
                    event_type=event_type,
                    status=status,
                    summary=summary,
                    detail=detail,
                    request_text=request_text,
                    request_deadline=request_deadline,
                )
            )
        EventManager.emit_event(
            activity_spec=activity_spec,
            notification_specs=notification_specs,
        )

    @staticmethod
    def generate_common_fields(request_id, event_type_friendly, is_succeeded, request_text=None, request_deadline=None, additional_info=None):
        ok_ng = 'OK' if is_succeeded else 'NG'
        status = EventStatus.SUCCEED if is_succeeded else EventStatus.FAILED
        title = "[Teams申請通知 / {}({}) / {}]".format(event_type_friendly, request_id, ok_ng)
        summary = summary = '{}に{}しました。'.format(
                event_type_friendly, EventStatus.to_friendly(status))
        if request_text:
            title += ' {}'.format(request_text)
        if request_deadline:
            if isinstance(request_deadline, datetime.datetime):
                title += ' (リリース希望日: {})'.format(request_deadline.strftime('%Y/%m/%d'))
            else:
                title += ' (リリース希望日: {})'.format(request_deadline)
        if additional_info:
            summary += '{}'.format(additional_info)
        return title, status, summary

    @staticmethod
    def _emit_event_on_start_job(db_session, user, request_id, request_category, request_operation, request_text, request_deadline, detail, is_succeeded):
        title, status, summary = AWXApiHelper.generate_common_fields(request_id, EventType.REQUEST_EXECUTE_STARTED_FRIENDLY, is_succeeded, request_text, request_deadline)
        sub_title = "申請({} / {})の実行が開始されました。".format(request_category, request_operation)
        sub_title2 = "申請 {} の実行が完了後、意図した変更が反映されたことをしてください。".format(request_id)
        AWXApiHelper._emit_event(
            db_session=db_session,
            notification_method=NotificationMethod.NOTIFY_TEMAS_AND_MAIL,
            title=title,
            sub_title=sub_title,
            sub_title2=sub_title2,
            user=user,
            request_id=request_id,
            event_type=EventType.REQUEST_EXECUTE_STARTED,
            status=status,
            summary=summary,
            detail=detail,
            request_text=request_text,
            request_deadline=request_deadline,
        )

    @staticmethod
    def _emit_event_on_job_completed(db_session, user, request_id, request_category, request_operation, request_text, request_deadline, detail, is_succeeded):
        title, status, summary = AWXApiHelper.generate_common_fields(request_id, EventType.REQUEST_EXECUTE_COMPLETED_FRIENDLY, is_succeeded, request_text, request_deadline)
        sub_title = "申請({} / {})が実行が完了しました。".format(request_category, request_operation)
        sub_title2 = "申請 {} の意図した変更が反映されたことを確認してください。".format(request_id)
        AWXApiHelper._emit_event(
            db_session=db_session,
            notification_method=NotificationMethod.NOTIFY_TEMAS_AND_MAIL,
            title=title,
            sub_title=sub_title,
            sub_title2=sub_title2,
            user=user,
            request_id=request_id,
            event_type=EventType.REQUEST_EXECUTE_COMPLETED,
            status=status,
            summary=summary,
            detail=detail,
            request_text=request_text,
            request_deadline=request_deadline,
        )
        