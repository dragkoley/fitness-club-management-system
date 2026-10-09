import json
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parent.parent
CONFIG_FILE_PATH = BASE_DIR / "config.json"


class AppSettings:
    def __init__(self):
        self.database_url: str = f"sqlite:///{BASE_DIR / 'fitness_club.db'}"
        self.log_file_path: Path = BASE_DIR / "logs" / "fitness_club.log"

        self._load_from_json()
        self._ensure_logs_dir_exists()

    def _load_from_json(self) -> None:
        if not CONFIG_FILE_PATH.exists():
            return

        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)

                db_name = data.get("DATABASE", {}).get("RELATIVE_PATH", "fitness_club.db")
                self.database_url = f"sqlite:///{BASE_DIR / db_name}"

                log_relative_path = data.get("LOGGING", {}).get("RELATIVE_PATH", "logs/fitness_club.log")
                self.log_file_path = BASE_DIR / log_relative_path

        except Exception as e:
            raise RuntimeError(f"Critical error while processing config file: {e}")

    def _ensure_logs_dir_exists(self) -> None:
        log_dir = self.log_file_path.parent
        log_dir.mkdir(parents=True, exist_ok=True)


settings = AppSettings()
