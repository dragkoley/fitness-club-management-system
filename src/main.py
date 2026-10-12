import sys

from PySide6.QtWidgets import QApplication

from src.database.seeders import seed_initial_data
from src.gui.main_window import FitnessClubMainWindow
from src.database.connection import DatabaseConnection
from src.utils.logger import AppLogger


def bootstrap_application() -> None:
    logger = AppLogger.get_instance()
    logger.log_info("Logger successfully started")
    logger.log_info("Fitness Club Management System is starting...")

    try:
        db = DatabaseConnection.get_instance()
        logger.log_info("Initializing database schema...")
        db.init_db()
        seed_initial_data()
    except Exception as e:
        logger.log_error("Application bootstrap failed with critical error: %s", e)
        sys.exit(1)

    logger.log_info("Database layers ready. Starting graphical user interface (PySide6)...")

    app = QApplication(sys.argv)
    main_window = FitnessClubMainWindow()
    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    bootstrap_application()
