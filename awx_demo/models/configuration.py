from sqlalchemy import Column, Integer, String

from awx_demo.db.base_class import Base

# from sqlalchemy.dialects.mysql import MEDIUMTEXT


class Configuration(Base):
    __tablename__ = "configurations"
    # __table_args__ = {'mysql_engine':'InnoDB', 'mysql_charset':'utf8mb4','mysql_collate':'utf8mb4_bin'}
    __table_args__ = {
        'comment': 'Global configurations'
    }

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False)
    value = Column(String(64), nullable=True)
