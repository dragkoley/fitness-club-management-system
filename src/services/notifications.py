from abc import ABC, abstractmethod
from datetime import date, timedelta

from src.database.orm_models import MemberORM
from src.utils.logger import AppLogger


class Observer(ABC):
    @abstractmethod
    def update(self, expiring_members: list[MemberORM]) -> None:
        raise NotImplementedError()

class Subject(ABC):
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, observer: Observer) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def  deattach(self, observer: Observer) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def notify(self, expiring_members: list[MemberORM]) -> None:
        for observer in self._observers:
            observer.update(expiring_members)


class SubscriptionNotification(Subject):

    def __init__(self, db_connection) -> None:
        super().__init__()
        self._db = db_connection
        self._logger = AppLogger.get_instance()

    def check_expiring_subscriptions(self, days_threshold: int = 5) -> list[MemberORM]:
        self._logger.log_info("[Observer] Checking expiring subscriptions...")
        session = self._db.open_session()
        expiring_members: list[MemberORM] = []

        try:
            today = date.today()
            target_date = today + timedelta(days=days_threshold)

            members = session.query(MemberORM).all()
            for member in members:
                if member.subscription:
                    if today <= member.subscription.end_date <= target_date:
                        expiring_members.append(member)

            self._logger.log_info("[Observer] Search finished. Found %d members", len(expiring_members))

            if expiring_members:
                self.notify(expiring_members)

        except Exception as e:
            self._logger.log_error("[Observer] Exception while checking expiring subscriptions: %s", e)

        finally:
            self._db.close_session(session, status=True)

class TerminalNotificationObserver(Observer):
    def update(self, expiring_members: list[MemberORM]) -> None:
        print("\n -----Terminal Notification Observer-----")
        print(f"{len(expiring_members)} members subscriptions require renewal sequence initiation.")
        members_id = [int(member.id) for member in expiring_members]
        print(f"Members: {members_id} ")
