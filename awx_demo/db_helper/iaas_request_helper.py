import copy
import datetime

from sqlalchemy import and_, asc, desc

from awx_demo.db import base
from awx_demo.db_helper.activity_helper import ActivityHelper
from awx_demo.db_helper.iaas_request_report_helper import IaasRequestReportHelper
from awx_demo.db_helper.types.request_status import RequestStatus
from awx_demo.notification.notification_spec import NotificationMethod, NotificationSpec
from awx_demo.notification.notificator import Notificator
from awx_demo.notification.teams_notificator import WARNING_ICON_FILE
from awx_demo.utils.event_helper import EventType
from awx_demo.utils.event_manager import EventManager


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
        detail = IaasRequestReportHelper.generate_request_detail(request)
        db_session.add(request)
        db_session.commit()

        IaasRequestHelper._emit_event_on_insert(
            db_session=db_session,
            user=session.get('awx_loginid'),
            request_id=request_id,
            request_category=request_category,
            request_operation=request_operation,
            request_text=request_text,
            request_deadline=request_deadline,
            detail=detail,
            is_succeeded=True
        )

    @staticmethod
    def duplicate_request(db_session, request_id, new_request_id, session):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()

        # 新しい申請レコードを作成し、各フィールドをコピーする
        new_request = base.IaasRequest()
        for column in base.IaasRequest.__table__.columns:
            setattr(new_request, column.name, getattr(request, column.name))
        new_request.id = None
        new_request.request_id = new_request_id
        db_session.add(new_request)
        detail = IaasRequestReportHelper.generate_request_detail(new_request)
        db_session.commit()
        
        IaasRequestHelper._emit_event_on_duplicate(
            db_session=db_session,
            user=session.get('awx_loginid'),
            request_id=request_id,
            request_id_new=new_request_id,
            request_category=new_request.request_category,
            request_operation=new_request.request_operation,
            request_text=request.request_text,
            request_deadline=request.request_deadline,
            detail=detail,
            is_succeeded=True
        )

    @staticmethod
    def update_request(db_session, request_id, request_deadline, request_text, job_options, request_status, iaas_user, session):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()

        # 更新前の申請内容を保存
        request_deadline_old = request.request_deadline
        request_text_old = request.request_text
        job_options_old = request.job_options
        request_status_old = request.request_status
        iaas_user_old = request.iaas_user

        request.request_deadline = request_deadline
        request.request_text = request_text
        request.job_options = job_options
        request.request_status = request_status
        request.iaas_user = iaas_user
        request_report = copy.deepcopy(request)
        detail = ''
        diff_changed = IaasRequestReportHelper.generate_diff_request(request, request_deadline_old, request_text_old, job_options_old, request_status_old, iaas_user_old)
        if diff_changed:
            detail = diff_changed + IaasRequestReportHelper.generate_request_detail(request)
        else:
            detail = IaasRequestReportHelper.generate_request_detail(request)
        db_session.commit()

        if diff_changed:
            IaasRequestHelper._emit_event_on_update(
                db_session=db_session,
                user=session.get('awx_loginid'),
                request_id=request_report.request_id,
                request_category=request_report.request_category,
                request_operation=request_report.request_operation,
                request_text=request_report.request_text,
                request_deadline=request_report.request_deadline,
                detail=detail,
                is_succeeded=True
            )
            if iaas_user != iaas_user_old:
                IaasRequestHelper._emit_event_on_update_iaas_user(
                    db_session=db_session,
                    user=session.get('awx_loginid'),
                    request_id=request_report.request_id,
                    request_category=request_report.request_category,
                    request_operation=request_report.request_operation,
                    request_text=request_text,
                    request_deadline=request_deadline,
                    additional_info='({} -> {})'.format(iaas_user_old,
                                                        iaas_user),
                    detail=detail,
                    is_succeeded=True,
                )
            if request_status != request_status_old:
                # ステータスが完了の場合、Teamsに加えてメールでも通知を行う
                notification_method = NotificationMethod.NOTIFY_TEMAS_AND_MAIL if request_report.request_status == RequestStatus.COMPLETED else NotificationMethod.NOTIFY_TEMAS_ONLY
                IaasRequestHelper._emit_event_on_update_request_status(
                    db_session=db_session,
                    user=session.get('awx_loginid'),
                    request_id=request_report.request_id,
                    request_category=request_report.request_category,
                    request_operation=request_report.request_operation,
                    request_text=request_text,
                    request_deadline=request_deadline,
                    additional_info='({} -> {})'.format(RequestStatus.to_friendly(
                        request_status_old), RequestStatus.to_friendly(request_status)),
                    detail=detail,
                    is_succeeded=True,
                    notification_method=notification_method,
                )
            else:
                # 変更がない場合は通知しない
                pass

    @staticmethod
    def update_request_status(db_session, request_id, request_status, session):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()
        # 更新前のステータスを取得
        request_status_current = request.request_status
    
        if request_status_current != request_status:
            request.request_status = request_status
            detail = IaasRequestReportHelper.generate_request_detail(request)
            request_report = copy.deepcopy(request)
            db_session.commit()

            # ステータスが完了の場合、Teamsに加えてメールでも通知を行う
            notification_method = NotificationMethod.NOTIFY_TEMAS_AND_MAIL if request_report.request_status == RequestStatus.COMPLETED else NotificationMethod.NOTIFY_TEMAS_ONLY

            IaasRequestHelper._emit_event_on_update_request_status(
                db_session=db_session,
                user=session.get('awx_loginid'),
                request_id=request_report.request_id,
                request_category=request_report.request_category,
                request_operation=request_report.request_operation,
                request_text=request_report.request_text,
                request_deadline=request_report.request_deadline,
                additional_info='({} -> {})'.format(RequestStatus.to_friendly(
                    request_status_current), RequestStatus.to_friendly(request_status)),
                detail=detail,
                is_succeeded=True,
                notification_method=notification_method,
            )
        else:
            pass

    @staticmethod
    def update_request_iaas_user(db_session, request_id, iaas_user, session):
        request = db_session.query(base.IaasRequest).filter(
            base.IaasRequest.request_id == request_id).first()
        # 更新前のIaaS作業担当者を取得
        iaas_user_current = request.iaas_user

        if iaas_user_current != iaas_user:
            request.iaas_user = iaas_user
            detail = IaasRequestReportHelper.generate_request_detail(request)
            db_session.commit()

            IaasRequestHelper._emit_event_on_update_iaas_user(
                db_session=db_session,
                user=session.get('awx_loginid'),
                request_id=request_id,
                request_category=request.request_category,
                request_operation=request.request_operation,
                request_text=request.request_text,
                request_deadline=request.request_deadline,
                additional_info='({} -> {})'.format(iaas_user_current, iaas_user),
                detail=detail,
                is_succeeded=True,
            )
        else:
            pass

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
        detail = IaasRequestReportHelper.generate_request_detail(request)
        db_session.commit()
        IaasRequestHelper._emit_event_on_delete(
            db_session=db_session,
            user=session.get('awx_loginid'),
            request_id=request_id, 
            request_category=request.request_category,
            request_operation=request.request_operation,
            request_text=request.request_text,
            request_deadline=request.request_deadline,
            detail=detail, 
            is_succeeded=True,
        )

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
    def _emit_event_on_insert(db_session, user, request_id, request_category, request_operation, request_text, request_deadline, detail, is_succeeded):
        title, status, summary = IaasRequestReportHelper.generate_common_fields(request_id, EventType.REQUEST_SENT_FRIENDLY, is_succeeded, request_text, request_deadline)
        sub_title = "新しい申請({} / {})が作成されました。".format(request_category, request_operation)
        sub_title2 = "申請 {} の内容を確認し、必要であれば変更を行なった上で承認し、作業を実施してください。".format(request_id)
        IaasRequestHelper._emit_event(
            db_session=db_session,
            notification_method=NotificationMethod.NOTIFY_TEMAS_AND_MAIL,
            title=title,
            sub_title=sub_title,
            sub_title2=sub_title2,
            user=user,
            request_id=request_id,
            event_type=EventType.REQUEST_SENT,
            status=status,
            summary=summary,
            detail=detail,
            request_text=request_text,
            request_deadline=request_deadline,
        )

    @staticmethod
    def _emit_event_on_duplicate(db_session, user, request_id, request_id_new, request_category, request_operation, request_text, request_deadline, detail, is_succeeded):
        title, status, summary = IaasRequestReportHelper.generate_common_fields(request_id, EventType.REQUEST_DUPLICATE_FRIENDLY, is_succeeded, request_text, request_deadline)
        sub_title = "申請({} / {})が複製されました。({} -> {})".format(request_category, request_operation, request_id, request_id_new)
        sub_title2 = "複製した申請 {} の内容を確認し、必要であれば変更を行なった上で承認し、作業を実施してください。".format(request_id_new)
        IaasRequestHelper._emit_event(
            db_session=db_session, 
            notification_method=NotificationMethod.NOTIFY_TEMAS_ONLY,
            title=title,
            sub_title=sub_title,
            sub_title2=sub_title2,
            user=user,
            request_id=request_id,
            event_type=EventType.REQUEST_DUPLICATE,
            status=status, 
            summary=summary,
            detail=detail,
            request_text=request_text,
            request_deadline=request_deadline,
        )
        IaasRequestHelper._emit_event_on_insert(
            db_session=db_session,
            user=user,
            request_id=request_id_new,
            request_category=request_category,
            request_operation=request_operation,
            request_text=request_text,
            request_deadline=request_deadline,
            detail=detail,
            is_succeeded=is_succeeded
        )

    @staticmethod
    def _emit_event_on_update(db_session, user, request_id, request_category, request_operation, request_text, request_deadline, detail, is_succeeded):
        title, status, summary = IaasRequestReportHelper.generate_common_fields(request_id, EventType.REQUEST_CHANGED_FRIENDLY, is_succeeded, request_text, request_deadline)
        sub_title = "申請({} / {})の内容が変更されました。".format(request_category, request_operation)
        sub_title2 = "申請 {} の内容を確認し、必要であれば変更を行なった上で承認し、作業を実施してください。".format(request_id)
        IaasRequestHelper._emit_event(
            db_session=db_session,
            notification_method=NotificationMethod.NOTIFY_TEMAS_ONLY,
            title=title,
            sub_title=sub_title,
            sub_title2=sub_title2,
            user=user,
            request_id=request_id,
            event_type=EventType.REQUEST_CHANGED,
            status=status,
            summary=summary,
            detail=detail,
            request_text=request_text,
            request_deadline=request_deadline,
        )

    @staticmethod
    def _emit_event_on_update_request_status(db_session, user, request_id, request_category, request_operation, request_text, request_deadline, additional_info, detail, is_succeeded, notification_method=NotificationMethod.NOTIFY_TEMAS_ONLY):
        title, status, summary = IaasRequestReportHelper.generate_common_fields(request_id, EventType.REQUEST_STATUS_CHANGED_FRIENDLY, is_succeeded, request_text, request_deadline, additional_info)
        sub_title = "申請({} / {})の状態が変更されました。".format(request_category, request_operation)
        sub_title2 = "申請 {} の内容を確認し、必要であれば変更を行なった上で承認し、作業を実施してください。".format(request_id)
        IaasRequestHelper._emit_event(
            db_session=db_session,
            notification_method=notification_method,
            title=title,
            sub_title=sub_title,
            sub_title2=sub_title2,
            user=user,
            request_id=request_id,
            event_type=EventType.REQUEST_STATUS_CHANGED,
            status=status,
            summary=summary,
            detail=detail,
            request_text=request_text,
            request_deadline=request_deadline,
        )

    @staticmethod
    def _emit_event_on_update_iaas_user(db_session, user, request_id, request_category, request_operation, request_text, request_deadline, additional_info, detail, is_succeeded):
        title, status, summary = IaasRequestReportHelper.generate_common_fields(request_id, EventType.REQUEST_IAAS_USER_ASSIGNED_FRIENDLY, is_succeeded, request_text, request_deadline, additional_info)
        sub_title = "申請({} / {})の作業担当者が変更されました。".format(request_category, request_operation)
        sub_title2 = "申請 {} の内容を確認し、必要であれば変更を行なった上で承認し、作業を実施してください。".format(request_id)
        IaasRequestHelper._emit_event(
            db_session=db_session,
            notification_method=NotificationMethod.NOTIFY_TEMAS_ONLY,
            title=title,
            sub_title=sub_title,
            sub_title2=sub_title2,
            user=user,
            request_id=request_id,
            event_type=EventType.REQUEST_IAAS_USER_ASSIGNED,
            status=status,
            summary=summary,
            detail=detail,
            request_text=request_text,
            request_deadline=request_deadline,
        )

    @staticmethod
    def _emit_event_on_delete(db_session, user, request_id, request_category, request_operation, request_text, request_deadline, detail, is_succeeded):
        title, status, summary = IaasRequestReportHelper.generate_common_fields(request_id, EventType.REQUEST_DELETED_FRIENDLY, is_succeeded, request_text, request_deadline)
        sub_title = "申請({} / {})が削除されました。".format(request_category, request_operation)
        sub_title2 = "申請 {} が削除されました。".format(request_id)
        IaasRequestHelper._emit_event(
            db_session=db_session,
            notification_method=NotificationMethod.NOTIFY_TEMAS_ONLY,
            title=title,
            sub_title=sub_title,
            sub_title2=sub_title2,
            user=user,
            request_id=request_id,
            event_type=EventType.REQUEST_DELETED,
            status=status,
            summary=summary,
            detail=detail,
            request_text=request_text,
            request_deadline=request_deadline,
            icon=WARNING_ICON_FILE,
        )
