from sqlalchemy.orm import Session

from database.connection import DatabaseConnection
from database.orm_models import MemberORM
from services.factories import SubscriptionIssuer, PaymentReceipt
from services.payment import PaymentMethod
from services.pricing import Discount
from utils.decorators import monitor_action
from utils.logger import AppLogger


class ClubManager:
    def __init__(self):
        self._db = DatabaseConnection.get_instance()

    @monitor_action
    def sell_subscription(self, member_id: int, sub_issuer: SubscriptionIssuer, discount_policy: Discount,
                          payment_method: PaymentMethod, receipt_factory: PaymentReceipt) -> bool:
        logger = AppLogger().get_instance()
        logger.log_info("[Facade] Processing subscription sale for member ID: %s", member_id)

        session: Session = self._db.open_session()
        status: bool = False

        try:
            member = session.get(MemberORM, member_id)
            if not member:
                logger.log_warning("[Facade] Aborted. Member with ID: %s not found in DB", member_id)
                return status

            new_subscription = sub_issuer.issue(discount_policy)
            is_approved = payment_method.process_transaction(new_subscription.price)

            new_payment = receipt_factory.create_record(
                amount=new_subscription.price,
                member_id=member_id,
                subscription_id=new_subscription.id,
                is_approved=is_approved
            )

            session.add(new_payment)

            if not is_approved:
                logger.log_warning("[Facade] Sale rejected due to transaction failure for member ID: %s", member_id)
                return status

            session.add(new_subscription)
            session.flush()
            member.subscription_id = new_subscription.id

            logger.log_info("[Facade] Subscription successfully assigned to member ID: %s", member_id)
            status = True
            return status

        except Exception as e:
            logger.log_error("[Facade] Failed to process subscription due to exception: %s", e)
            status = False
            return status

        finally:
            self._db.close_session(session, status)
