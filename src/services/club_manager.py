from datetime import date

from sqlalchemy.orm import Session

from src.database.connection import DatabaseConnection
from src.database.orm_models import MemberORM
from src.services.factories import MonthlySubscriptionIssuer, YearSubscriptionIssuer, \
    CardPaymentReceipt, CashPaymentReceipt
from src.services.payment import CashPayment, CardPayment
from src.services.pricing import NoDiscount, StudentDiscount, CorporateDiscount
from src.utils.decorators import monitor_action
from src.utils.logger import AppLogger


class ClubManager:
    def __init__(self):
        self._db = DatabaseConnection.get_instance()
        self._logger = AppLogger.get_instance()

        self._subscription_issuers = {
            "monthly": MonthlySubscriptionIssuer,
            "year": YearSubscriptionIssuer
        }

        self._receipt_factories = {
            "card": CardPaymentReceipt,
            "cash": CashPaymentReceipt
        }

        self._payment_methods = {
            "cash": CashPayment,
            "card": CardPayment
        }

        self._discount_policies = {
            "none": NoDiscount,
            "student": StudentDiscount,
            "corporate": CorporateDiscount
        }

    @monitor_action
    def sell_subscription(self, member_id: int, subscription_type: str,
                          payment_method: str, discount_type: str = "none") -> bool:
        self._logger.log_info("[Facade] Processing subscription sale for member ID: %s", member_id)

        session: Session = self._db.open_session()
        status: bool = False

        try:
            member = session.get(MemberORM, member_id)
            if not member:
                self._logger.log_warning("[Facade] Aborted. Member with ID: %s not found in DB", member_id)
                return status

            issuer = self._subscription_issuers[subscription_type]()
            payment = self._payment_methods[payment_method]()
            receipt_factory = self._receipt_factories[payment_method]()
            discount = self._discount_policies[discount_type]()

            new_subscription = issuer.issue(discount)
            session.add(new_subscription)
            session.flush()

            is_approved = payment.process_transaction(new_subscription.price)

            new_payment = receipt_factory.create_record(
                amount=new_subscription.price,
                member_id=member_id,
                subscription_id=new_subscription.id,
                is_approved=is_approved
            )

            session.add(new_payment)

            if not is_approved:
                self._logger.log_warning("[Facade] Sale rejected due to transaction failure for member ID: %s",
                                         member_id)
                return False

            member.subscription_id = new_subscription.id

            self._logger.log_info("[Facade] Subscription successfully assigned to member ID: %s", member_id)
            status = True

        except Exception as e:
            self._logger.log_error("[Facade] Failed to process subscription due to exception: %s", e)
            status = False

        finally:
            self._db.close_session(session, status)

        return status

    @monitor_action
    def register_member(self, full_name: str, birth_date: date, phone: str ) -> bool:
        self._logger.log_info("[Facade] Registering member with full name: %s", full_name)

        session: Session = self._db.open_session()
        status: bool = False

        try:
            existing_member = session.query(MemberORM).filter_by(phone=phone.strip()).first()
            if existing_member:
                self._logger.log_warning("[Facade] Registration aborted. Phone %s already exists", phone)
                return status

            new_member = MemberORM(
                full_name=full_name.strip(),
                birth_date=birth_date,
                phone=phone.strip()
            )

            session.add(new_member)
            self._logger.log_info("[Facade] Member %s successfully created in session context", full_name)
            status = True

        except Exception as e:
            self._logger.log_error("[Facade] Failed to register member: %s", e)
            status = False

        finally:
            self._db.close_session(session, status)

        return status
