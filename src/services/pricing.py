from abc import ABC, abstractmethod

from utils.logger import AppLogger


class Discount(ABC):
    @abstractmethod
    def apply(self, base_price: int) -> int:
        pass


class NoDiscount(Discount):
    def apply(self, base_price: int) -> int:
        logger = AppLogger().get_instance()
        logger.log_info("[Strategy] Applying standard pricing policy. Base price: %s", base_price)
        return base_price


class StudentDiscount(Discount):
    def apply(self, base_price: int) -> int:
        logger = AppLogger().get_instance()
        discount: int = int(base_price * 0.20)
        final = base_price - discount
        logger.log_info("[Strategy] Applying student pricing policy. Base: %s, Discount: %s, Final: %s",
                        base_price, discount, final)
        return final


class CorporateDiscount(Discount):
    def apply(self, base_price: int) -> int:
        logger = AppLogger().get_instance()
        discount: int = int(base_price * 0.15)
        final = base_price - discount
        logger.log_info("[Strategy] Applying corporate pricing policy. Base price: %s, Discount: %s, Final: %s",
                        base_price, discount, final)
        return final
