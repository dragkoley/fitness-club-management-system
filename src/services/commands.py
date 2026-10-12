from abc import ABC, abstractmethod
from datetime import date

from src.services.club_manager import ClubManager
from src.utils.logger import AppLogger


class Command(ABC):

    @abstractmethod
    def execute(self) -> bool:
        raise NotImplementedError()


class ExecuteSubscriptionSale(Command):
    def __init__(self, manager: ClubManager, member_id: int, subscription_type: str, payment_method: str,
                 discount_type: str) -> None:
        self._manager = manager
        self._member_id = member_id
        self._subscription_type = subscription_type
        self._payment_method = payment_method
        self._discount_type = discount_type
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info(
            "[Command] Triggering subscription sale processing for member ID: %s", self._member_id)
        return self._manager.sell_subscription(
            member_id=self._member_id,
            subscription_type=self._subscription_type,
            payment_method=self._payment_method,
            discount_type=self._discount_type
        )


class ExecuteMemberRegistration(Command):
    def __init__(self, manager: ClubManager, full_name: str, birth_date: date, phone: str) -> None:
        self._manager = manager
        self._full_name = full_name
        self._birth_date = birth_date
        self._phone = phone
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering member (%s) registration", self._full_name)
        return self._manager.register_member(
            full_name=self._full_name,
            birth_date=self._birth_date,
            phone=self._phone
        )
