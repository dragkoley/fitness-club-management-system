from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session, MappedAsDataclass

from config.settings import settings
from src.utils.logger import AppLogger


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class DatabaseConnection:
    _instance = None

    def __init__(self):
        if DatabaseConnection._instance is not None:
            raise Exception('This class is a singleton. Use method get_instance()')

        self.engine = create_engine(
            settings.database_url,
            echo=True,
            connect_args={"check_same_thread": False},
        )
        self.SessionFactory = sessionmaker(bind=self.engine)

    @staticmethod
    def get_instance() -> DatabaseConnection:
        if DatabaseConnection._instance is None:
            DatabaseConnection._instance = DatabaseConnection()
        return DatabaseConnection._instance

    def open_session(self) -> Session:
        logger = AppLogger.get_instance()
        logger.log_info("Opening database connection")
        return self.SessionFactory()

    def close_session(self, session: Session, status: bool) -> None:
        logger = AppLogger.get_instance()

        try:
            if status:
                session.commit()
                logger.log_info("Transaction committed successfully")
            else:
                session.rollback()
                logger.log_info("Transaction rollback successfully")
        finally:
            session.close()
            logger.log_info("Database connection closed")

    def init_db(self) -> None:
        Base.metadata.create_all(self.engine)
