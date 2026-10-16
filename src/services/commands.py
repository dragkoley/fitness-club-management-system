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


class ExecuteTrainerRegistration(Command):
    def __init__(self, manager: ClubManager, full_name: str, phone: str, speciality: str, experience: str) -> None:
        self._manager = manager
        self._full_name = full_name
        self._phone = phone
        self._speciality = speciality
        self._experience = experience
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering trainer (%s) registration", self._full_name)
        return self._manager.register_trainer(
            full_name=self._full_name,
            speciality=self._speciality,
            experience=self._experience,
            phone=self._phone
        )

class ExecuteTrainingCreation(Command):
    def __init__(self, manager: ClubManager, name: str, training_type: str, duration_minutes: int) -> None:
        self._manager = manager
        self._name = name
        self._training_type = training_type
        self._duration_minutes = duration_minutes
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering training %s creation", self._name)
        return self._manager.create_training(
            name=self._name,
            training_type=self._training_type,
            duration_minutes=self._duration_minutes
        )

class ExecuteScheduleCreation(Command):
    def __init__(self, manager: ClubManager, training_date: date, trainer_id: int, training_id: int) -> None:
        self._manager = manager
        self._training_date = training_date
        self._trainer_id = trainer_id
        self._training_id = training_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering schedule creation for trainer ID: %s", self._trainer_id)
        return self._manager.create_schedule(
            training_date=self._training_date,
            trainer_id=self._trainer_id,
            training_id=self._training_id
        )

class ExecuteTrainingBooking(Command):
    def __init__(self, manager: ClubManager, member_id: int, schedule_id: int) -> None:
        self._manager = manager
        self._member_id = member_id
        self._schedule_id = schedule_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering training booking for member ID: %s", self._member_id)
        return self._manager.book_training(
            member_id=self._member_id,
            schedule_id=self._schedule_id
        )