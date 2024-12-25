from datetime import datetime

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import DateTime

from awx_demo.db.base_class import Base


# from sqlalchemy.dialects.mysql import MEDIUMTEXT

class Activity(Base):
    __tablename__ = "activities"
    # __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4','mysql_collate':'utf8mb4_bin'}
    __table_args__ = {
        'comment': 'User activities'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(32), nullable=False)
    request_id = Column(String(32), nullable=True)
    activity_type = Column(String(32), nullable=False)
    status = Column(String(32), nullable=False)
    summary = Column(String(128), nullable=False)
    detail = Column(String(512), nullable=False)
    created = Column(DateTime, default=datetime.now, nullable=False)
    updated = Column(DateTime, default=datetime.now,
                     onupdate=datetime.now, nullable=False)
