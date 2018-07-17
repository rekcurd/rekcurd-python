from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import exists
from utils.env_loader import (
    TEST_MODE,
    DB_MODE,
    DB_MYSQL_HOST,
    DB_MYSQL_PORT,
    DB_MYSQL_DBNAME,
    DB_MYSQL_USER,
    DB_MYSQL_PASSWORD,
    SERVICE_NAME,
    FILE_MODEL,
    DIR_MODEL,
    APPLICATION_NAME
)


def db_url():
    """ Get full URL for DB

    :TODO: Make configuarable of template of URL and encoding
    :TODO: Use Enum for DB_MODE
    :TODO: Use an appropriate "Exception"
    """
    if DB_MODE == "sqlite":
        db_name = "db.test.sqlite3" if TEST_MODE else "db.sqlite3"
        url = f'sqlite:///{db_name}'
    elif DB_MODE == "mysql":
        host = DB_MYSQL_HOST
        port = DB_MYSQL_PORT
        db_name = "test_"+DB_MYSQL_DBNAME if TEST_MODE else DB_MYSQL_DBNAME
        user = DB_MYSQL_USER
        password = DB_MYSQL_PASSWORD
        url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8'
    else:
        raise Exception("Invalid DB_MODE.")
    return url


class DAO(object):
    """ Data Access Object

    This implementation is inspired by Flask-SQLAlchemy's one.
    """

    def __init__(self):
        self.engine = create_engine(
            db_url(),
            encoding='utf-8',
            echo=True
        )

        self.session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        )

        self.ModelBase = declarative_base()


db = DAO()

from models.model_assignment import ModelAssignment

if TEST_MODE:
    db.ModelBase.metadata.drop_all(db.engine)
db.ModelBase.metadata.create_all(db.engine)

if not db.session.query(exists().where(ModelAssignment.service_name == SERVICE_NAME)).scalar():
    model_assignment = ModelAssignment()
    model_assignment.service_name = SERVICE_NAME
    model_assignment.model_path = FILE_MODEL
    model_assignment.first_boot = True
    db.session.add(model_assignment)
    db.session.commit()


def get_model_path(model_path: str = None):
    if model_path is None:
        model_path = FILE_MODEL

        result = db.session.query(ModelAssignment). \
            filter(ModelAssignment.service_name == SERVICE_NAME). \
            one_or_none()

        if result is not None:
            model_path = result.model_path
    return "{0}/{1}/{2}".format(DIR_MODEL, APPLICATION_NAME, model_path)


SERVICE_FIRST_BOOT = True
try:
    model_assignment = db.session.query(ModelAssignment).filter(ModelAssignment.service_name == SERVICE_NAME).one()
    SERVICE_FIRST_BOOT = model_assignment.first_boot
except:
    pass
