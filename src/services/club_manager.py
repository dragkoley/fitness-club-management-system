from datetime import date

from sqlalchemy.orm import Session, joinedload

from src.database.connection import DatabaseConnection
from src.database.orm_models import MemberORM, TrainerORM, TrainingORM, ScheduleORM, VisitORM
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
    def register_member(self, full_name: str, birth_date: date, phone: str) -> bool:
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

    def delete_member(self, member_id: int) -> bool:
        self._logger.log_info("[Facade] Deleting member with ID: %s", member_id)

        session = self._db.open_session()
        status: bool = False

        try:
            member = session.get(MemberORM, member_id)
            if not member:
                self._logger.log_warning("[Facade] Aborted. Member ID: %s not found in db", member_id)
                return status

            session.delete(member)
            self._logger.log_info("[Facade] Member %s successfully deleted in session context", member_id)
            status = True

        except Exception as e:
            self._logger.log_error("[Facade] Failed to delete member: %s", e)
            status = False

        finally:
            self._db.close_session(session, status)

        return status

    def update_member(self, member_id: int, full_name: str, phone: str) -> bool:
        self._logger.log_info("[Facade] Updating member with ID: %s", member_id)

        session = self._db.open_session()
        status = False

        try:
            cleaned_phone = phone.strip()
            existing_phone_owner = session.query(MemberORM).filter(
                MemberORM.phone == cleaned_phone, MemberORM.id != member_id).first()

            if existing_phone_owner:
                self._logger.log_warning("[Facade] Update aborted. Phone %s already exists", cleaned_phone)
                return status

            member = session.get(MemberORM, member_id)
            if not member:
                self._logger.log_warning("[Facade] Member with ID: %s not found in db", member_id)
                return status

            member.full_name = full_name
            member.phone = cleaned_phone

            self._logger.log_info("[Facade] Member %s successfully updated in session context", member_id)
            status = True

        except Exception as e:
            self._logger.log_error("[Facade] Failed to update member: %s", e)
            status = False

        finally:
            self._db.close_session(session, status)

        return status

    def register_trainer(self, full_name: str, phone: str, speciality: str, experience: str) -> bool:
        self._logger.log_info("[Facade] Registering trainer with full name: %s", full_name)

        session: Session = self._db.open_session()
        status: bool = False

        try:
            new_trainer = TrainerORM(
                full_name=full_name,
                phone=phone,
                specialty=speciality,
                experience=experience
            )

            session.add(new_trainer)
            self._logger.log_info("[Facade] Trainer %s successfully created in session contexti", full_name)
            status = True

        except Exception as e:
            self._logger.log_error("[Facade] Failed to register trainer: %s", e)
            statis = False

        finally:
            self._db.close_session(session, status)

        return status

    def create_training(self, name: str, training_type: str, duration_minutes: int) -> bool:
        self._logger.log_info("[Facade] Creating training with name: %s", name)

        session: Session = self._db.open_session()
        status = False

        try:
            new_training = TrainingORM(
                name=name,
                type=training_type,
                duration_minutes=duration_minutes
            )

            session.add(new_training)
            self._logger.log_info("[Facade] Training %s successfully created", name)
            status = True

        except Exception as e:
            self._logger.log_error("[Facade] Failed to create training: %s", e)
            status = False

        finally:
            self._db.close_session(session, status)

        return status

    def create_schedule(self, training_date: date, trainer_id: int, training_id: int) -> bool:
        self._logger.log_info("[Facade] Creating schedule with training date: %s", training_date)

        session: Session = self._db.open_session()
        status = False

        try:
            new_schedule = ScheduleORM(
                date=training_date,
                trainer_id=trainer_id,
                training_id=training_id
            )

            session.add(new_schedule)
            self._logger.log_info("[Facade] Schedule %s successfully created", training_date)
            status = True

        except Exception as e:
            self._logger.log_error("[Facade] Failed to create schedule: %s", e)
            status = False

        finally:
            self._db.close_session(session, status)

        return status

    def book_training(self, schedule_id: int, member_id: int) -> bool:
        self._logger.log_info("[Facade] Booking training schedule: %s", schedule_id)

        session: Session = self._db.open_session()
        status = False

        try:
            member = session.get(MemberORM, member_id)
            if not member or not member.subscription_id:
                self._logger.log_warning("[Facade] Booking rejected. Member has no active subscription or not exist")
                return status

            if member.subscription.end_date < date.today():
                self._logger.log_warning("[Facade] Booking rejected. Subscription expired on %s",
                                         member.subscription.end_date)
                return status

            schedule_entry = session.get(ScheduleORM, schedule_id)
            if not schedule_entry:
                self._logger.log_warning("[Facade] Booking rejected. Schedule with ID %s not found", schedule_id)
                return status

            current_booking_counts = session.query(VisitORM).filter_by(training_id=schedule_entry.training_id,
                                                                       date=schedule_entry.date).count()
            if current_booking_counts >= 15:
                self._logger.log_warning("[Facade] Booking rejected. Schedule with ID %s is fully booked", schedule_id)
                return status

            member_visit_count = session.query(VisitORM).filter_by(member_id=member_id, date=schedule_entry.date,
                                                                   training_id=schedule_entry.training_id).count()
            if member_visit_count >= 1:
                self._logger.log_warning("[Facade] Booking rejected. Member already booked this training")
                return status

            new_visit = VisitORM(
                date=schedule_entry.date,
                training_id=schedule_entry.training_id,
                member_id=member_id
            )

            session.add(new_visit)
            self._logger.log_info("[Facade] Booking successfully confirmed for member ID %s", member_id)
            status = True

        except Exception as e:
            self._logger.log_error("[Facade] Failed to book schedule: %s", e)
            status = False

        finally:
            self._db.close_session(session, status)

        return status
