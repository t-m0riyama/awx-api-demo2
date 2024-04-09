import datetime
import json
import random
from pprint import pprint

from awx_demo.db import base, db
from awx_demo.utils.doc_id_utils import DocIdUtils

DUCUMENT_ID_LENGTH = 7

if __name__ == "__main__":
    # ジェネレータから要素を取得
    session = db.get_db()

    job_options = {
        'vsphere_cluster': 'cluster-99',
        'target_vms': 'vm01,vm02',
        'vcpus': 8,
        'memory_gb': 16,
        # 'change_vm_cpu_enabled': 'True',
        # 'change_vm_memory_enabled': 'True',
        'shutdown_before_change': True,
        'startup_after_change': True,
    }
    # request
    for i in range(0, 30, 1):
        datetime_str = "2024/1/1 00:00:00"
        datetime_formatted = datetime.datetime.strptime(
            datetime_str, "%Y/%m/%d %H:%M:%S") + datetime.timedelta(days=i)
        deadline_days = i + int(random.uniform(7, 30))
        datetime_deadline_formatted = datetime.datetime.strptime(
            datetime_str, "%Y/%m/%d %H:%M:%S") + datetime.timedelta(days=deadline_days)
        request = base.IaasRequest(
            id=i,
            request_id=DocIdUtils.generate_id(DUCUMENT_ID_LENGTH),
            request_date=datetime_formatted,
            request_deadline=datetime_deadline_formatted,
            request_user='moriyama',
            iaas_user='moriyama',
            request_category='サーバに対する変更',
            request_operation='CPUコア/メモリ割り当て変更',
            request_text='ABC{}システム向けWEBサーバCPU/メモリ増設'.format(i),
            job_options=json.dumps(job_options),
            request_status='request start',
        )
        session.add(request)

    session.commit()

    # ユーザーの取得
    rows = session.query(base.IaasRequest).offset(0).limit(10).all()
    for row in rows:
        pprint(row.__dict__)

    # ユーザーの削除
    # request = session.query(base.IaasRequest).filter(base.IaasRequest.id == 1).first()
    # session.delete(request)
    # session.commit()
