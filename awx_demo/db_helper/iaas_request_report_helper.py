import copy
import datetime
import json

import yaml

from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.utils.event_helper import EventStatus


class IaasRequestReportHelper:

    # const
    REQUEST_KEYS = [
        "request_id",
        "request_date",
        "request_deadline",
        "request_user",
        "request_category",
        "request_operation",
        "request_text",
        "request_status",
        "iaas_user",
        "job_options",
        "job_id",
        "updated",
    ]
    REQUEST_FRIENDLY_KEYS = [
        "申請ID",
        "申請日",
        "リリース希望日",
        "申請者",
        "依頼区分",
        "申請項目",
        "依頼内容",
        "ステータス",
        "作業担当者",
        "ジョブ設定",
        "ジョブID",
        "最終更新日",
    ]
    JOB_OPTIONS_KEYS = [
        "vsphere_cluster",
        "target_vms",
        "vcpus",
        "memory_gb",
        "change_vm_cpu_enabled",
        "change_vm_memory_enabled",
        "shutdown_before_change",
        "startup_after_change",        
    ]
    JOB_OPTIONS_FRIENDLY_KEYS = [
        "クラスタ名",
        "仮想マシン名",
        "CPUコア数",
        "メモリ容量（GB)",
        "CPUコア数の変更",
        "メモリ容量の変更",
        "設定変更前に、仮想マシンを停止する",
        "設定変更後に、仮想マシンを起動する",
    ]
    
    @classmethod
    def diff_request_change(cls, request, request_deadline_old, request_text_old, job_options_old, request_status_old, iaas_user_old):
        diff_request = {}
        if request.request_text != request_text_old:
            diff_request['request_text'] = '{} -> {}'.format(request_text_old, request.request_text)
        if request.request_deadline != request_deadline_old:
            diff_request['request_deadline'] = '{} -> {}'.format(request_deadline_old.strftime('%Y/%m/%d'), request.request_deadline.strftime('%Y/%m/%d'))
        if request.request_status != request_status_old:
            diff_request['request_status'] = '{} -> {}'.format(RequestStatus.to_friendly(request_status_old), RequestStatus.to_friendly(request.request_status))
        if request.iaas_user != iaas_user_old:
            diff_request['iaas_user'] = '{} -> {}'.format(iaas_user_old, request.iaas_user)
        job_options_dict = cls.diff_job_options(request.job_options, job_options_old)
        if job_options_dict != {}:
            diff_request['job_options'] = job_options_dict

        return diff_request

    @classmethod
    def diff_job_options(cls, job_options, job_options_old):
        diff_job_options = {}
        job_options_dict = json.loads(job_options)
        job_options_old_dict = json.loads(job_options_old)
        for key in job_options_dict.keys():
            if job_options_dict[key] != job_options_old_dict[key]:
                diff_job_options[key] = '{} -> {}'.format(job_options_old_dict[key], job_options_dict[key])
        return diff_job_options

    @classmethod
    def generate_request_detail(cls, request):
        request_report = copy.deepcopy(request)
        request_report.job_options = json.loads(request_report.job_options)
        return "\n== 申請内容の詳細一覧 =============\n" + cls.to_friendly_request(vars(request_report))

    @classmethod
    def generate_diff_request(cls, request, request_deadline_old, request_text_old, job_options_old, request_status_old, iaas_user_old):
        diff_request = cls.diff_request_change(
            request=request,
            request_deadline_old=request_deadline_old,
            request_text_old=request_text_old,
            job_options_old=job_options_old,
            request_status_old=request_status_old,
            iaas_user_old=iaas_user_old,
        )
        print(diff_request)
        if diff_request != {}:
            return "\n== 変更内容の詳細 =============\n" + cls.to_friendly_request(diff_request)
        else:
            return None

    @classmethod
    def generate_common_fields(cls, request_id, event_type_friendly, is_succeeded, request_text=None, request_deadline=None, additional_info=None):
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

    @classmethod
    def to_friendly_request(cls, request, default_value=None):
        request_friendry = {}
        for i, request_key in enumerate(cls.REQUEST_KEYS):
            if request.get(request_key):
                if isinstance(request[request_key], datetime.datetime):
                    request_friendry[cls.REQUEST_FRIENDLY_KEYS[i]] = request.pop(request_key, default_value).strftime('%Y/%m/%d')
                else:
                    request_friendry[cls.REQUEST_FRIENDLY_KEYS[i]] = request.pop(request_key, default_value)
        if request_friendry.get("ジョブ設定"):
            request_friendry["ジョブ設定"] = cls.to_friendly_job_options(job_options_str=json.dumps(request_friendry["ジョブ設定"]), convert_to_yaml=False)
        yaml_string = yaml.safe_dump(data=request_friendry, allow_unicode=True, sort_keys=False)
        return yaml_string

    @classmethod
    def to_friendly_job_options(cls, job_options_str, convert_to_yaml=True, default_value=None):
        job_options_dict = json.loads(job_options_str)
        for i, job_options_key in enumerate(cls.JOB_OPTIONS_KEYS):
            if job_options_dict.get(job_options_key):
                job_options_dict[cls.JOB_OPTIONS_FRIENDLY_KEYS[i]] = job_options_dict.pop(job_options_key, default_value)

        if convert_to_yaml:
            # YAML文字列として返却
            yaml_string = yaml.safe_dump(data=job_options_dict, allow_unicode=True, sort_keys=False)
            return yaml_string
        else:
            # ディクショナリとして返却
            return job_options_dict
