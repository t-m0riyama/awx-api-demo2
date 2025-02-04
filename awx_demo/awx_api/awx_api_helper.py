import datetime
import json
import os
from distutils.util import strtobool

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

    API_SUCCEEDED = "AWX_API_SUCCEEDED"
    API_FAILED_STATUS = "AWX_API_FAILED_STATUS"
    API_FAILED_TO_CONNECT = "AWX_API_FAILED_TO_CONNECT"
    API_FAILED_OTHER = "AWX_API_FAILED_OTHER"

    HTTP_PROXY_DEFAULT  = "http://proxy.example.com:8080"
    HTTPS_PROXY_DEFAULT = "http://proxy.example.com:8080"
    AWX_PROXIES = {
        "http"  : os.getenv("RMX_AWX_HTTP_PROXY", HTTP_PROXY_DEFAULT),
        "https" : os.getenv("RMX_AWX_HTTPS_PROXY", os.getenv("RMX_AWX_HTTP_PROXY", HTTPS_PROXY_DEFAULT)),
    }
    AWX_PROXY_ENABLED = bool(strtobool(os.getenv("RMX_AWX_PROXY_ENABLED", "False")))

    @classmethod
    @Logging.func_logger
    def _request_get(cls, request_url, headers, loginid, password, verify, proxy_enabled):
        if proxy_enabled:
            response = requests.get(request_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=verify, proxies=cls.AWX_PROXIES)
        else:
            response = requests.get(request_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=verify)
        return response

    @classmethod
    @Logging.func_logger
    def _request_post(cls, request_url, headers, loginid, password, verify, data, proxy_enabled):
        if proxy_enabled:
            response = requests.post(request_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=verify, data=data, proxies=cls.AWX_PROXIES)
        else:
            response = requests.post(request_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=verify, data=data)
        return response

    @classmethod
    @Logging.func_logger
    def login(cls, uri_base, loginid, password):
        request_url = uri_base + '/api/v2/me/'
        headers = {'Content-Type': 'application/json'}
        try:
            response = cls._request_get(request_url=request_url, headers=headers, loginid=loginid, password=password, verify=False, proxy_enabled=cls.AWX_PROXY_ENABLED)
            Logging.info(f'AWX_LOGIN_URL: {request_url}')
            Logging.info(f'AWX_LOGIN_STATUS: {str(response.status_code)} / {request_url}')
            if response.status_code == 200:
                return True, cls.API_SUCCEEDED
            else:
                return False, cls.API_FAILED_STATUS
        except Exception as e:
            Logging.error(f'{cls.API_FAILED_TO_CONNECT}: {request_url}')
            Logging.error(e)
            return False, cls.API_FAILED_TO_CONNECT

    @classmethod
    @Logging.func_logger
    def get_teams_user_belong(cls, uri_base, loginid, password):
        request_url = uri_base + '/api/v2/me/'
        headers = {'Content-Type': 'application/json'}
        try:
            response_me = cls._request_get(request_url=request_url, headers=headers, loginid=loginid, password=password, verify=False, proxy_enabled=cls.AWX_PROXY_ENABLED)
            if response_me.status_code != 200:
                Logging.error("Failed to retrieve information for user")
                return False

            teams_url = uri_base + \
                jmespath.search("results[0].related.teams", response_me.json())
            Logging.info(f'AWX_TEAMS_URL: {teams_url}')
            response_teams = cls._request_get(request_url=teams_url, headers=headers, loginid=loginid, password=password, verify=False, proxy_enabled=cls.AWX_PROXY_ENABLED)

            if response_teams.status_code != 200:
                Logging.error(f'AWX_TEAMS_STATUS: {response_teams.status_code} / {teams_url}')
                Logging.error("Failed to retrieve information for teams")
                return False
            Logging.info(f'AWX_TEAMS_STATUS: {response_teams.status_code} / {teams_url}')

            teams = []
            for team_name in jmespath.search("results[].name", response_teams.json()):
                teams.append(team_name)
            return teams
        except Exception as e:
            Logging.error(e)
            return None

    @classmethod
    @Logging.func_logger
    def get_users(cls, uri_base, loginid, password, filtered_users=None):
        request_url = uri_base + '/api/v2/users/'
        headers = {'Content-Type': 'application/json'}
        if not filtered_users:
            filtered_users = []

        try:
            response = cls._request_get(request_url=request_url, headers=headers, loginid=loginid, password=password, verify=False, proxy_enabled=cls.AWX_PROXY_ENABLED)
            if response.status_code == 200:
                users = []
                result_users = jmespath.search('results', response.json())
                for user in result_users:
                    if user['username'] not in filtered_users:
                        users.append(user)
                return users
            else:
                return None
        except Exception as e:
            Logging.error(e)
            return None

    @classmethod
    @Logging.func_logger
    def get_user(cls, uri_base, loginid, password, user_name, filtered_users=None):
        request_url = uri_base + '/api/v2/users/'
        headers = {'Content-Type': 'application/json'}
        if not filtered_users:
            filtered_users = []

        try:
            response = cls._request_get(request_url=request_url, headers=headers, loginid=loginid, password=password, verify=False, proxy_enabled=cls.AWX_PROXY_ENABLED)
            if response.status_code == 200:
                result_users = jmespath.search('results', response.json())
                for user in result_users:
                    if user['username'] in filtered_users:
                        continue
                    if user['username'] == user_name:
                        return user
            else:
                return None
        except Exception as e:
            Logging.error(e)
            return None

    @classmethod
    @Logging.func_logger
    def start_job(cls, uri_base, loginid, password, job_template_name, request, job_options, session):
        headers = {'Content-Type': 'application/json'}
        vars_json = cls.generate_vars(job_options)
        try:
            job_template_id = cls.get_job_template_id(
                uri_base, loginid, password, job_template_name)
            launch_url = uri_base + \
                '/api/v2/job_templates/{}/launch/'.format(job_template_id)
            # ジョブテンプレートが見つからない場合は、エラー終了
            if job_template_id == cls.JOB_TEMPLATE_ID_NOT_FOUND:
                Logging.error(f'AWX_TEMPLATE_NOT_FOUND: {job_template_name}')
                return cls.JOB_LAUNCH_FAILED

            Logging.info(f'AWX_LAUNCH_URL: {launch_url}')
            Logging.info(f'AWX_LAUNCH_VARS: {vars_json} / {launch_url}')
            detail = IaasRequestReportHelper.generate_request_detail(request, job_options)
            response = cls._request_post(
                request_url=launch_url, headers=headers, loginid=loginid, password=password, verify=False, data=vars_json, proxy_enabled=cls.AWX_PROXY_ENABLED)
            if response.status_code == 201:
                response_results = jmespath.search('job', response.json())
                cls._emit_event_on_start_job(
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
                Logging.info(f'AWX_LAUNCH_STATUS: {response.status_code} / {launch_url}')
                Logging.info(f'AWX_LAUNCH_JOB_ID: {str(response_results)} / {launch_url}')
                # Logging.info(f'AWX_LAUNCH_RESPONSE: {response.text} / {launch_url}')
                return response_results
            else:
                cls._emit_event_on_start_job(
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
                Logging.error(f'AWX_LAUNCH_STATUS: {response.status_code} / {launch_url}')
                Logging.error(f'AWX_LAUNCH_RESPONSE: {response.text} / {launch_url}')
                return cls.JOB_LAUNCH_FAILED
        except Exception as e:
            Logging.error(e)
            return cls.JOB_LAUNCH_CONNECTION_FAILED

    @classmethod
    @Logging.func_logger
    def generate_vars(cls, job_options):
        return json.dumps({"extra_vars": job_options})

    @classmethod
    @Logging.func_logger
    def get_job_template_id(cls, uri_base, loginid, password, job_template_name):
        job_templates_url = uri_base + '/api/v2/job_templates/{}/'.format(job_template_name)
        headers = {'Content-Type': 'application/json'}
        try:
            Logging.info(f'AWX_JOB_TEMPLATE_URL: {job_templates_url}')
            response = cls._request_get(request_url=job_templates_url, headers=headers, loginid=loginid, password=password, verify=False, proxy_enabled=cls.AWX_PROXY_ENABLED)
            if response.status_code == 200:
                Logging.info(f'AWX_JOB_TEMPLATE_STATUS: {response.status_code} / {job_templates_url}')
                Logging.info(f'AWX_JOB_TEMPLATE_ID: {(response.json())["id"]} / {job_templates_url}')
                return (response.json())['id']
            else:
                Logging.error(f'AWX_JOB_TEMPLATE_STATUS: {response.status_code} / {job_templates_url}')
                return cls.JOB_TEMPLATE_ID_NOT_FOUND
        except Exception as e:
            Logging.error(e)
            return cls.JOB_TEMPLATE_ID_CONNECTION_FAILED

    @classmethod
    @Logging.func_logger
    def get_job_status(cls, uri_base, loginid, password, request, job_id, session):
        job_status_url = uri_base + '/api/v2/jobs/{}/'.format(job_id)
        headers = {'Content-Type': 'application/json'}
        Logging.info(f'AWX_JOB_STATUS_URL: {job_status_url}')
        detail = IaasRequestReportHelper.generate_request_detail(request)
        try:
            response = cls._request_get(
                request_url=job_status_url, headers=headers, loginid=loginid, password=password, verify=False, proxy_enabled=cls.AWX_PROXY_ENABLED)
            Logging.info(f'AWX_JOB_STATUS_STATUS: {str(response.status_code)} / {job_status_url}')
            if response.status_code == 200:
                job_status = jmespath.search('status', response.json())
                job_status_succeed = True if job_status == cls.JOB_STATUS_SUCCEEDED else False
                Logging.info(f'AWX_JOB_STATUS: {str(job_status)} / {job_status_url}')
                if job_status == cls.JOB_STATUS_SUCCEEDED or job_status == cls.JOB_STATUS_FAILED:
                    cls._emit_event_on_job_completed(
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
                cls._emit_event_on_job_completed(
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
                return str(cls.JOB_STATUS_FAILED)
        except Exception as e:
            Logging.error(e)
            cls._emit_event_on_job_completed(
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
            return str(cls.JOB_STATUS_CONNECTION_FAILED)

    @classmethod
    def _emit_event(cls, db_session, notification_method: NotificationMethod, title, sub_title, sub_title2, user, request_id, event_type, status, summary, detail='', request_text=None, request_deadline=None, icon=None):
        activity_spec = ActivityHelper.ActivitySpec(
            db_session=db_session,
            user=user,
            request_id=request_id,
            activity_type=event_type,
            status=status,
            summary=summary,
            detail=detail,
        )

        notification_specs = []
        # Teams通知を指定された場合
        if notification_method == NotificationMethod.NOTIFY_TEAMS_ONLY or notification_method == NotificationMethod.NOTIFY_TEAMS_AND_MAIL:
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
        if notification_method == NotificationMethod.NOTIFY_MAIL_ONLY or notification_method == NotificationMethod.NOTIFY_TEAMS_AND_MAIL:
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

    @classmethod
    @Logging.func_logger
    def generate_common_fields(cls, request_id, event_type_friendly, is_succeeded, request_text=None, request_deadline=None, additional_info=None):
        ok_ng = 'OK' if is_succeeded else 'NG'
        status = EventStatus.SUCCEED if is_succeeded else EventStatus.FAILED
        title = "[申請通知 / {}({}) / {}]".format(event_type_friendly, request_id, ok_ng)
        summary = '{}に{}しました。'.format(
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

    @classmethod
    def _emit_event_on_start_job(cls, db_session, user, request_id, request_category, request_operation, request_text, request_deadline, detail, is_succeeded):
        title, status, summary = cls.generate_common_fields(request_id, EventType.REQUEST_EXECUTE_STARTED_FRIENDLY, is_succeeded, request_text, request_deadline)
        sub_title = "申請({} / {})の実行が開始されました。".format(request_category, request_operation)
        sub_title2 = "申請 {} の実行が完了後、意図した変更が反映されたことをしてください。".format(request_id)
        cls._emit_event(
            db_session=db_session,
            notification_method=NotificationMethod.NOTIFY_TEAMS_AND_MAIL,
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

    @classmethod
    def _emit_event_on_job_completed(cls, db_session, user, request_id, request_category, request_operation, request_text, request_deadline, detail, is_succeeded):
        title, status, summary = cls.generate_common_fields(request_id, EventType.REQUEST_EXECUTE_COMPLETED_FRIENDLY, is_succeeded, request_text, request_deadline)
        sub_title = "申請({} / {})が実行が完了しました。".format(request_category, request_operation)
        sub_title2 = "申請 {} の意図した変更が反映されたことを確認してください。".format(request_id)
        cls._emit_event(
            db_session=db_session,
            notification_method=NotificationMethod.NOTIFY_TEAMS_AND_MAIL,
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
