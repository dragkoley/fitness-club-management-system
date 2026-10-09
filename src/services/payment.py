from abc import ABC, abstractmethod

from utils.logger import AppLogger


class PaymentMethod(ABC):
    @abstractmethod
    def process_transaction(self, amount: int) -> bool:
        pass


class CashPayment(PaymentMethod):
    def process_transaction(self, amount: int) -> bool:
        logger = AppLogger().get_instance()
        logger.log_info("[Strategy] Initializing cash payment process for amount: %s rub", amount)
        return True


class CardPayment(PaymentMethod):
    def process_transaction(self, amount: int) -> bool:
        logger = AppLogger().get_instance()
        logger.log_info("[Strategy] Initializing card payment process for amount: %s rub", amount)
        logger.log_info("[Strategy] Card transaction approved by acquiring bank for amount: %s rub", amount)
        return True
