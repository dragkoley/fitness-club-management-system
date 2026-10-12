import logging
import sys


class AppLogger:
    _instance = None

    def __init__(self):
        if AppLogger._instance is not None:
            raise Exception('Class AppLogger is a singleton. Use method get_instance()')

        self._logger = logging.getLogger("FitnessClubLogger")
        self._logger.setLevel(logging.INFO)

        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

        # file_handler = logging.FileHandler(settings.log_file_path, encoding="utf-8")
        # file_handler.setFormatter(formatter)
        # self._logger.addHandler(file_handler)
        if not self._logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            self._logger.addHandler(console_handler)

    @staticmethod
    def get_instance() -> AppLogger:
        if AppLogger._instance is None:
            AppLogger._instance = AppLogger()
        return AppLogger._instance

    def log_info(self, message: str, *args) -> None:
        self._logger.info(message, *args)

    def log_warning(self, message: str, *args) -> None:
        self._logger.warning(message, *args)

    def log_error(self, message: str, *args) -> None:
        self._logger.error(message, *args)
