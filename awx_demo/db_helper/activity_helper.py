from sqlalchemy import and_, asc, desc

from awx_demo.db import base, db


class ActivityHelper:

    @staticmethod
    def add_activity(db_session=None, user=None, request_id=None, activity_type=None, status=None, summary=None, detail=None):
        db_session, is_fallback = ActivityHelper.fallback_db_session(
            db_session)
        request = base.Activity(
            user=user,
            request_id=request_id,
            activity_type=activity_type,
            status=status,
            summary=summary,
            detail=detail,
        )
        db_session.add(request)
        db_session.commit()

        if not is_fallback:
            db_session.close()

    @staticmethod
    def fallback_db_session(db_session):
        is_fallback = False
        if db_session is None:
            db_session = db.get_db()
            is_fallback = True
        return (db_session, is_fallback)

    @staticmethod
    def count_activities(db_session, filters):
        # filters中のNoneなど無効な要素を削除
        filters = list(filter(lambda x: x is not None, filters))
        return db_session.query(base.Activity).filter(*filters).count()

    @staticmethod
    def get_activities(db_session, filters, orderspec, offset_row, limit_rows):
        # filters中のNoneなど無効な要素を削除
        filters = list(filter(lambda x: x is not None, filters))
        requests_data = db_session.query(base.Activity).filter(
            *filters).order_by(orderspec).offset(offset_row).limit(limit_rows).all()
        return requests_data

    @staticmethod
    def get_activity(db_session, request_id):
        request_data = db_session.query(base.Activity).filter(
            base.Activity.request_id == request_id).first()
        return request_data

    @staticmethod
    def get_filter_user(user):
        if user:
            return and_(base.Activity.user == user)
        else:
            return None

    @staticmethod
    def get_filter_activity_type(activity_type):
        if activity_type:
            return and_(base.Activity.activity_type == activity_type)
        else:
            return None

    @staticmethod
    def get_filter_summary(summary_contains):
        if summary_contains:
            return and_(base.Activity.summary.contains(summary_contains))
        else:
            return None

    @staticmethod
    def get_filter_status(statuses):
        if statuses:
            return and_(base.Activity.status.in_(statuses))
        else:
            return None

    @staticmethod
    def get_orderspec_activity_type(is_asc):
        return asc(base.Activity.activity_type) if is_asc else desc(base.Activity.activity_type)

    @staticmethod
    def get_orderspec_request_id(is_asc):
        return asc(base.Activity.request_id) if is_asc else desc(base.Activity.request_id)

    @staticmethod
    def get_orderspec_created(is_asc):
        return asc(base.Activity.created) if is_asc else desc(base.Activity.created)

    @staticmethod
    def get_orderspec_user(is_asc):
        return asc(base.Activity.user) if is_asc else desc(base.Activity.user)

    @staticmethod
    def get_orderspec_summary(is_asc):
        return asc(base.Activity.summary) if is_asc else desc(base.Activity.summary)

    @staticmethod
    def get_orderspec_detail(is_asc):
        return asc(base.Activity.detail) if is_asc else desc(base.Activity.detail)
