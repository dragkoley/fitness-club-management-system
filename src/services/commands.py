from abc import ABC, abstractmethod

from services.club_manager import ClubManager
from utils.logger import AppLogger


class Command(ABC):

    @abstractmethod
    def execute(self) -> bool:
        pass


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
