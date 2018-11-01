# coding: utf-8


from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from drucker.utils import DruckerConfig


class DruckerDAO(object):
    """ Data Access Object

    This implementation is inspired by Flask-SQLAlchemy's one.
    """

    def __init__(self, config: DruckerConfig = None):
        """
        Constructor
        :param config:
        """
        self.config = config
        self.engine = create_engine(
            'sqlite:///:memory:',
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
        if config is not None:
            self.init_app(config)

    def init_app(self, config: DruckerConfig):
        self.config = config
        self.engine = create_engine(
            self.__db_url(config),
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

    def __db_url(self, config: DruckerConfig):
        """ Get full URL for DB

        :TODO: Make configuarable of template of URL and encoding
        :TODO: Use Enum for DB_MODE
        :TODO: Use an appropriate "Exception"
        """
        if config.DB_MODE == "sqlite":
            db_name = "drucker.test.sqlite3" if config.TEST_MODE else "drucker.sqlite3"
            url = f'sqlite:///{db_name}'
        elif config.DB_MODE == "mysql":
            host = config.DB_MYSQL_HOST
            port = config.DB_MYSQL_PORT
            db_name = "test_"+config.DB_MYSQL_DBNAME if config.TEST_MODE else config.DB_MYSQL_DBNAME
            user = config.DB_MYSQL_USER
            password = config.DB_MYSQL_PASSWORD
            url = f'mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}?charset=utf8'
        else:
            raise Exception("Invalid DB_MODE.")
        return url


db = DruckerDAO()
