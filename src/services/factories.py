from abc import ABC, abstractmethod
from datetime import date, timedelta

from src.database.orm_models import SubscriptionORM, PaymentORM
from src.services.pricing import Discount
from src.utils.logger import AppLogger


class SubscriptionIssuer(ABC):
    @abstractmethod
    def issue(self, discount_policy: Discount) -> SubscriptionORM:
        raise NotImplementedError()


class MonthlySubscriptionIssuer(SubscriptionIssuer):
    def issue(self, discount_policy: Discount) -> SubscriptionORM:
        logger = AppLogger.get_instance()
        logger.log_info("[Factory method] Generating data structures for 30-day subscription")
        start = date.today()
        end = start + timedelta(days=30)
        base_price = 3000
        final_price = discount_policy.apply(base_price)
        logger.log_info("[Factory method] Subscription object. Type: Monthly, Final Price: %s", final_price)
        return SubscriptionORM(
            type="Monthly",
            start_date=start,
            end_date=end,
            price=final_price
        )


class YearSubscriptionIssuer(SubscriptionIssuer):
    def issue(self, discount_policy: Discount) -> SubscriptionORM:
        logger = AppLogger.get_instance()
        logger.log_info("[Factory method] Generating data structures for 365-day subscription")
        start = date.today()
        end = start + timedelta(days=365)
        base_price = 25000
        final_price = discount_policy.apply(base_price)
        logger.log_info("[Factory method] Subscription object. Type: Yearly, Final Price: %s", final_price)
        return SubscriptionORM(
            type="Yearly",
            start_date=start,
            end_date=end,
            price=final_price
        )


class PaymentReceipt(ABC):
    @abstractmethod
    def create_record(self, amount: int, member_id: int, subscription_id: int, is_approved: bool) -> PaymentORM:
        raise NotImplementedError()


class CashPaymentReceipt(PaymentReceipt):
    def create_record(self, amount: int, member_id: int, subscription_id: int, is_approved: bool) -> PaymentORM:
        logger = AppLogger.get_instance()
        logger.log_info("[Factory method] Preparing cash payment database record for member ID: %s", member_id)
        return PaymentORM(
            value=amount,
            member_id=member_id,
            subscription_id=subscription_id,
            status="Success" if is_approved else "Declined",
            type="Cash",
        )


class CardPaymentReceipt(PaymentReceipt):
    def create_record(self, amount: int, member_id: int, subscription_id: int, is_approved: bool) -> PaymentORM:
        logger = AppLogger.get_instance()
        logger.log_info("[Factory method] Preparing card payment database record for member ID: %s", member_id)
        return PaymentORM(
            value=amount,
            member_id=member_id,
            subscription_id=subscription_id,
            status="Success" if is_approved else "Declined",
            type="Card",
        )
