import datetime

from sqlalchemy import and_, asc, desc

from awx_demo.db import base
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.db_helper.types.activity_type import ActivityStatus, ActivityType
from awx_demo.db_helper.types.request_status import RequestStatus


class IaasRequestHelper:

    @staticmethod
    def add_request(db_session, request_id, request_deadline, request_user, request_category, request_operation, request_text, job_options, request_status, session):
        request = base.IaasRequest(
            request_id=request_id,
            request_date=datetime.datetime.now(),
            request_deadline=request_deadline,
            request_user=request_user,
            request_category=request_category,
            request_operation=request_operation,
            request_text=request_text,
            job_options=job_options,
            request_status=request_status,
        )
        db_session.add(request)
        db_session.commit()
        IaasRequestHelper._add_activity_on_insert(
            db_session, session.get('awx_loginid'), session.get('request_id'), True)

    @staticmethod
    def update_request(db_session, request_id, request_deadline, request_text, job_options, request_status, iaas_user, session):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()

        # 更新前のIaaS作業担当者とステータスを取得
        iaas_user_current = request.iaas_user
        request_status_current = request.request_status

        request.request_deadline = request_deadline
        # request.request_category=request_category
        # request.request_operation=request_operation
        request.request_text = request_text
        request.job_options = job_options
        request.request_status = request_status
        request.iaas_user = iaas_user
        db_session.commit()
        IaasRequestHelper._add_activity_on_update(
            db_session, session.get('awx_loginid'), session.get('request_id'), True)
        if iaas_user != iaas_user_current:
            IaasRequestHelper._add_activity_on_update_iaas_user(
                db_session=db_session,
                user=session.get('awx_loginid'),
                request_id=session.get('request_id'),
                additional_info='({} -> {})'.format(iaas_user_current,
                                                    iaas_user),
                is_succeeded=True,
            )
        if request_status != request_status_current:
            IaasRequestHelper._add_activity_on_update_request_status(
                db_session=db_session,
                user=session.get('awx_loginid'),
                request_id=session.get('request_id'),
                additional_info='({} -> {})'.format(RequestStatus.to_friendly(
                    request_status_current), RequestStatus.to_friendly(request_status)),
                is_succeeded=True,
            )

    @staticmethod
    def update_request_status(db_session, request_id, request_status, session):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()
        # 更新前のステータスを取得
        request_status_current = request.request_status
        request.request_status = request_status
        db_session.commit()
        IaasRequestHelper._add_activity_on_update_request_status(
            db_session=db_session,
            user=session.get('awx_loginid'),
            request_id=request_id,
            additional_info='({} -> {})'.format(RequestStatus.to_friendly(
                request_status_current), RequestStatus.to_friendly(request_status)),
            is_succeeded=True,
        )

    @staticmethod
    def update_request_iaas_user(db_session, request_id, iaas_user, session):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()
        # 更新前のIaaS作業担当者を取得
        iaas_user_current = request.iaas_user
        request.iaas_user = iaas_user
        db_session.commit()
        IaasRequestHelper._add_activity_on_update_iaas_user(
            db_session=db_session,
            user=session.get('awx_loginid'),
            request_id=request_id,
            additional_info='({} -> {})'.format(iaas_user_current, iaas_user),
            is_succeeded=True,
        )

    @staticmethod
    def update_job_id(db_session, request_id, job_id):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()
        request.job_id = job_id
        db_session.commit()

    @staticmethod
    def delete_request(db_session, request_id, session):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()
        db_session.delete(request)
        db_session.commit()
        IaasRequestHelper._add_activity_on_delete(
            db_session, session.get('awx_loginid'), request_id, True)

    @staticmethod
    def count_requests(db_session, filters):
        # filters中のNoneなど無効な要素を削除
        filters = list(filter(lambda x: x is not None, filters))
        return db_session.query(base.IaasRequest).filter(*filters).count()

    @staticmethod
    def get_requests(db_session, filters, orderspec, offset_row, limit_rows):
        # filters中のNoneなど無効な要素を削除
        filters = list(filter(lambda x: x is not None, filters))
        requests_data = db_session.query(base.IaasRequest).filter(
            *filters).order_by(orderspec).offset(offset_row).limit(limit_rows).all()
        return requests_data

    @staticmethod
    def get_request(db_session, request_id):
        request_data = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()
        return request_data

    @staticmethod
    def get_filter_iaas_user(request_user):
        if request_user:
            return and_(base.IaasRequest.iaas_user == request_user)
        else:
            return None

    @staticmethod
    def get_filter_request_user(request_user):
        if request_user:
            return and_(base.IaasRequest.request_user == request_user)
        else:
            return None

    @staticmethod
    def get_filter_request_text(request_text_contains):
        if request_text_contains:
            return and_(base.IaasRequest.request_text.contains(request_text_contains))
        else:
            return None

    @staticmethod
    def get_filter_request_status(request_statuses):
        if request_statuses:
            return and_(base.IaasRequest.request_status.in_(request_statuses))
        else:
            return None

    @staticmethod
    def get_orderspec_request_id(is_asc):
        return asc(base.IaasRequest.request_id) if is_asc else desc(base.IaasRequest.request_id)

    @staticmethod
    def get_orderspec_request_deadline(is_asc):
        return asc(base.IaasRequest.request_deadline) if is_asc else desc(base.IaasRequest.request_deadline)

    @staticmethod
    def get_orderspec_updated(is_asc):
        return asc(base.IaasRequest.updated) if is_asc else desc(base.IaasRequest.updated)

    @staticmethod
    def get_orderspec_request_user(is_asc):
        return asc(base.IaasRequest.request_user) if is_asc else desc(base.IaasRequest.request_user)

    @staticmethod
    def get_orderspec_iaas_user(is_asc):
        return asc(base.IaasRequest.iaas_user) if is_asc else desc(base.IaasRequest.iaas_user)

    @staticmethod
    def get_orderspec_request_operation(is_asc):
        return asc(base.IaasRequest.request_operation) if is_asc else desc(base.IaasRequest.request_operation)

    @staticmethod
    def get_orderspec_request_text(is_asc):
        return asc(base.IaasRequest.request_text) if is_asc else desc(base.IaasRequest.request_text)

    @staticmethod
    def _add_activity(db_session, user, request_id, activity_type, status, summary, detail=''):
        ActivityHelper.add_activity(
            db_session=db_session,
            user=user,
            request_id=request_id,
            activity_type=activity_type,
            status=status,
            summary=summary,
            detail=detail,
        )

    @staticmethod
    def _add_activity_on_insert(db_session, user, request_id, is_succeeded):
        status = ActivityStatus.SUCCEED if is_succeeded else ActivityStatus.FAILED
        summary = '{}に{}しました。'.format(
            ActivityType.REQUEST_SENT_FRIENDLY, ActivityStatus.to_friendly(status))
        IaasRequestHelper._add_activity(
            db_session, user, request_id, ActivityType.REQUEST_SENT, status, summary)

    @staticmethod
    def _add_activity_on_update(db_session, user, request_id, is_succeeded):
        status = ActivityStatus.SUCCEED if is_succeeded else ActivityStatus.FAILED
        summary = '{}に{}しました。'.format(
            ActivityType.REQUEST_CHANGED_FRIENDLY, ActivityStatus.to_friendly(status))
        IaasRequestHelper._add_activity(
            db_session, user, request_id, ActivityType.REQUEST_CHANGED, status, summary)

    @staticmethod
    def _add_activity_on_update_request_status(db_session, user, request_id, additional_info, is_succeeded):
        status = ActivityStatus.SUCCEED if is_succeeded else ActivityStatus.FAILED
        summary = '{}に{}しました。{}'.format(
            ActivityType.REQUEST_STATUS_CHANGED_FRIENDLY, ActivityStatus.to_friendly(status), additional_info)
        IaasRequestHelper._add_activity(
            db_session, user, request_id, ActivityType.REQUEST_STATUS_CHANGED, status, summary)

    @staticmethod
    def _add_activity_on_update_iaas_user(db_session, user, request_id, additional_info, is_succeeded):
        status = ActivityStatus.SUCCEED if is_succeeded else ActivityStatus.FAILED
        summary = '{}に{}しました。{}'.format(
            ActivityType.REQUEST_IAAS_USER_ASSIGNED_FRIENDLY, ActivityStatus.to_friendly(status), additional_info)
        IaasRequestHelper._add_activity(
            db_session, user, request_id, ActivityType.REQUEST_IAAS_USER_ASSIGNED, status, summary)

    @staticmethod
    def _add_activity_on_delete(db_session, user, request_id, is_succeeded):
        status = ActivityStatus.SUCCEED if is_succeeded else ActivityStatus.FAILED
        summary = '{}に{}しました。'.format(
            ActivityType.REQUEST_DELETED_FRIENDLY, ActivityStatus.to_friendly(status))
        IaasRequestHelper._add_activity(
            db_session, user, request_id, ActivityType.REQUEST_DELETED, status, summary)
