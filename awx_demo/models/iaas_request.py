from datetime import datetime

from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.sql.sqltypes import DateTime

from awx_demo.db.base_class import Base

# from sqlalchemy.dialects.mysql import MEDIUMTEXT


class IaasRequest(Base):
    __tablename__ = "iaas_requests"
    # __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4','mysql_collate':'utf8mb4_bin'}
    __table_args__ = {
        'comment': 'IaaS requests'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(String(32), nullable=False)
    request_date = Column(DateTime, default=datetime.now, nullable=False)
    request_deadline = Column(DateTime, nullable=False)
    request_user = Column(String(32), nullable=False)
    iaas_user = Column(String(32), nullable=True)
    request_status = Column(
        String(32), default='request start', nullable=False)
    request_category = Column(String(255), nullable=False)
    request_operation = Column(String(255), nullable=False)
    request_text = Column(String(255), nullable=False)
    job_options = Column(JSON, nullable=False)
    job_id = Column(Integer, nullable=True)
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now,
                     onupdate=datetime.now, nullable=False)
