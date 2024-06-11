import json

import jmespath
import requests
from requests.auth import HTTPBasicAuth

from awx_demo.db import db
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.utils.event_helper import EventStatus, EventType
from awx_demo.utils.logging import Logging


class AWXApiHelper:

    # const
    JOB_TEMPLATE_ID_NOT_FOUND = -1
    JOB_TEMPLATE_ID_CONNECTION_FAILED = -2
    JOB_LAUNCH_FAILED = -3
    JOB_LAUNCH_CONNECTION_FAILED = -4
    JOB_STATUS_FAILED = -5
    JOB_STATUS_CONNECTION_FAILED = -6

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
    def start_job(uri_base, loginid, password, job_template_name, job_options, session):
        headers = {'Content-Type': 'application/json'}
        vars_json = AWXApiHelper.generate_vars(job_options)
        try:
            job_template_id = AWXApiHelper.get_job_template_id(
                uri_base, loginid, password, job_template_name)
            launch_url = uri_base + \
                '/api/v2/job_templates/{}/launch/'.format(job_template_id)
            Logging.info('launch_url: ' + launch_url)
            Logging.info('vars: ' + vars_json)
            response = requests.post(launch_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=False, data=vars_json)
            if response.status_code == 201:
                response_results = jmespath.search('job', response.json())
                Logging.info('job_id: ' + str(response_results))
                AWXApiHelper._add_activity_on_start_job(
                    db.get_db(), session.get('awx_loginid'), session.get('request_id'), True)
                return response_results
            else:
                AWXApiHelper._add_activity_on_start_job(
                    db.get_db(), session.get('awx_loginid'), session.get('request_id'), False)
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
    def get_job_status(uri_base, loginid, password, job_id, session):
        job_status_url = uri_base + '/api/v2/jobs/{}/'.format(job_id)
        headers = {'Content-Type': 'application/json'}
        Logging.info('job_status_url: ' + job_status_url)
        try:
            response = requests.get(job_status_url, headers=headers, auth=HTTPBasicAuth(
                loginid, password), verify=False)
            Logging.info('job_status_status: ' + str(response.status_code))
            Logging.info('job_state: ' + jmespath.search('status', response.json()))
            if response.status_code == 200:
                job_status = jmespath.search('status', response.json())
                Logging.info("job_status: " + str(job_status))
                if job_status == 'successful':
                    AWXApiHelper._add_activity_on_job_completed(
                        db.get_db(), session.get('awx_loginid'), session.get('request_id'), True)
                elif job_status == 'failed':
                    AWXApiHelper._add_activity_on_job_completed(
                        db.get_db(), session.get('awx_loginid'), session.get('request_id'), False)
                return job_status
            else:
                AWXApiHelper._add_activity_on_job_completed(
                    db.get_db(), session.get('awx_loginid'), session.get('request_id'), False)
                return str(AWXApiHelper.JOB_STATUS_FAILED)
        except Exception as e:
            Logging.error(e)
            AWXApiHelper._add_activity_on_job_completed(
                db.get_db(), session.get('awx_loginid'), session.get('request_id'), False)
            return str(AWXApiHelper.JOB_STATUS_CONNECTION_FAILED)

    @staticmethod
    def _add_activity(db_session, user, request_id, event_type, status, summary, detail=''):
        ActivityHelper.add_activity(
            db_session=db_session,
            user=user,
            request_id=request_id,
            event_type=event_type,
            status=status,
            summary=summary,
            detail=detail,
        )

    @staticmethod
    def _add_activity_on_start_job(db_session, user, request_id, is_succeeded):
        status = EventStatus.SUCCEED if is_succeeded else EventStatus.FAILED
        summary = '{}に{}しました。'.format(
            EventType.REQUEST_EXECUTE_STARTED_FRIENDLY, EventStatus.to_friendly(status))
        AWXApiHelper._add_activity(
            db_session, user, request_id, EventType.REQUEST_EXECUTE_STARTED, status, summary)

    @staticmethod
    def _add_activity_on_job_completed(db_session, user, request_id, is_succeeded):
        status = EventStatus.SUCCEED if is_succeeded else EventStatus.FAILED
        summary = '{}に{}しました。'.format(
            EventType.REQUEST_EXECUTE_COMPLETED_FRIENDLY, EventStatus.to_friendly(status))
        AWXApiHelper._add_activity(
            db_session, user, request_id, EventType.REQUEST_EXECUTE_COMPLETED, status, summary)
