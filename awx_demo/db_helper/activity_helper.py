from sqlalchemy import and_, asc, desc

from awx_demo.db import base, db
from awx_demo.utils.logging import Logging


class ActivityHelper:

    class ActivitySpec:
        def __init__(self, db_session=None, user=None, request_id=None, activity_type=None, status=None, summary=None, detail=None):
            self.db_session = db_session
            self.user = user
            self.request_id = request_id
            self.activity_type = activity_type
            self.status = status
            self.summary = summary
            self.detail = detail

    @classmethod
    @Logging.func_logger
    def add_activity(cls, activity_spec: ActivitySpec):
        db_session, is_fallback = cls.fallback_db_session(
            activity_spec.db_session)
        request = base.Activity(
            user=activity_spec.user,
            request_id=activity_spec.request_id,
            activity_type=activity_spec.activity_type,
            status=activity_spec.status,
            summary=activity_spec.summary,
            detail=activity_spec.detail,
        )
        db_session.add(request)
        db_session.commit()

        if is_fallback:
            db_session.close()

    @staticmethod
    @Logging.func_logger
    def fallback_db_session(db_session):
        is_fallback = False
        if db_session is None:
            db_session = db.get_db()
            is_fallback = True
        return db_session, is_fallback

    @staticmethod
    @Logging.func_logger
    def count_activities(db_session, filters):
        # filters中のNoneなど無効な要素を削除
        filters = list(filter(lambda x: x is not None, filters))
        return db_session.query(base.Activity).filter(*filters).count()

    @staticmethod
    @Logging.func_logger
    def get_activities(db_session, filters, orderspec, offset_row, limit_rows):
        # filters中のNoneなど無効な要素を削除
        filters = list(filter(lambda x: x is not None, filters))
        requests_data = db_session.query(base.Activity).filter(
            *filters).order_by(orderspec).offset(offset_row).limit(limit_rows).all()
        return requests_data

    @staticmethod
    @Logging.func_logger
    def get_activity(db_session, request_id):
        request_data = db_session.query(base.Activity).filter(
            base.Activity.request_id == request_id).first()
        return request_data

    @staticmethod
    @Logging.func_logger
    def get_filter_user(user):
        return and_(base.Activity.user == user) if user else None

    @staticmethod
    @Logging.func_logger
    def get_filter_activity_type(activity_type):
        return and_(base.Activity.activity_type == activity_type) if activity_type else None

    @staticmethod
    @Logging.func_logger
    def get_filter_summary(summary_contains):
        return and_(base.Activity.summary.contains(summary_contains)) if summary_contains else None

    @staticmethod
    @Logging.func_logger
    def get_filter_status(statuses):
        return and_(base.Activity.status.in_(statuses)) if statuses else None

    @staticmethod
    @Logging.func_logger
    def get_orderspec_activity_type(is_asc):
        return asc(base.Activity.activity_type) if is_asc else desc(base.Activity.activity_type)

    @staticmethod
    @Logging.func_logger
    def get_orderspec_request_id(is_asc):
        return asc(base.Activity.request_id) if is_asc else desc(base.Activity.request_id)

    @staticmethod
    @Logging.func_logger
    def get_orderspec_created(is_asc):
        return asc(base.Activity.created) if is_asc else desc(base.Activity.created)

    @staticmethod
    @Logging.func_logger
    def get_orderspec_user(is_asc):
        return asc(base.Activity.user) if is_asc else desc(base.Activity.user)

    @staticmethod
    @Logging.func_logger
    def get_orderspec_summary(is_asc):
        return asc(base.Activity.summary) if is_asc else desc(base.Activity.summary)

    @staticmethod
    @Logging.func_logger
    def get_orderspec_detail(is_asc):
        return asc(base.Activity.detail) if is_asc else desc(base.Activity.detail)
