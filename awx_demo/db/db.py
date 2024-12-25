import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_URL = 'sqlite:///data/iaas_requests.sqlite3??charset=utf8'
engine = sqlalchemy.create_engine(
    DB_URL,
    # echo=True,
)

# session initialize
session_local = sessionmaker(autocommit=False, autoflush=True, bind=engine)


def get_db():
    return session_local()
