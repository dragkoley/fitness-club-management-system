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

class ExecuteBookingCancellation(Command):
    def __init__(self, manager: ClubManager, visit_id: int) -> None:
        self._manager = manager
        self._visit_id = visit_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering cancel booking for visit ID: %s", self._visit_id)
        return self._manager.cancel_booking(
            visit_id=self._visit_id
        )


class ExecuteMemberDeletion(Command):
    def __init__(self, manager: ClubManager, member_id: int) -> None:
        self._manager = manager
        self._member_id = member_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering member deletion for member ID: %s", self._member_id)
        return self._manager.delete_member(
            member_id=self._member_id
        )


class ExecuteMemberUpdate(Command):
    def __init__(self, manager: ClubManager, member_id: int, full_name: str, phone: str, birth_date: date) -> None:
        self._manager = manager
        self._member_id = member_id
        self._full_name = full_name
        self._phone = phone
        self._birth_date = birth_date
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering update for member ID: %s", self._member_id)
        return self._manager.update_member(
            member_id=self._member_id,
            full_name=self._full_name,
            phone=self._phone,
            birth_date=self._birth_date
        )

class ExecuteSubscriptionCancellation(Command):
    def __init__(self, manager: ClubManager, member_id: int) -> None:
        self._manager = manager
        self._member_id = member_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering cancellation for member ID: %s", self._member_id)
        return self._manager.cancel_subscription(
            member_id=self._member_id
        )

class ExecuteTrainingDeletion(Command):
    def __init__(self, manager: ClubManager, training_id: int) -> None:
        self._manager = manager
        self._training_id = training_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering deletion for training ID: %s", self._training_id)
        return self._manager.delete_training(
            training_id=self._training_id
        )

class ExecuteScheduleDeletion(Command):
    def __init__(self, manager: ClubManager, schedule_id: int) -> None:
        self._manager = manager
        self._schedule_id = schedule_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering schedule deletion for ID: %s", self._schedule_id)
        return self._manager.delete_schedule(schedule_id=self._schedule_id)

class ExecuteTrainerDeletion(Command):
    def __init__(self, manager: ClubManager, trainer_id: int) -> None:
        self._manager = manager
        self._trainer_id = trainer_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering trainer deletion for ID: %s", self._trainer_id)
        return self._manager.delete_trainer(trainer_id=self._trainer_id)

class ExecuteTrainerUpdate(Command):
    def __init__(self, manager: ClubManager, trainer_id: int, full_name: str, phone: str, speciality: str, experience: str) -> None:
        self._manager = manager
        self._trainer_id = trainer_id
        self._full_name = full_name
        self._phone = phone
        self._speciality = speciality
        self._experience = experience
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering update for trainer ID: %s", self._trainer_id)
        return self._manager.update_trainer(
            trainer_id=self._trainer_id,
            full_name=self._full_name,
            phone=self._phone,
            speciality=self._speciality,
            experience=self._experience
        )

class ExecuteLockerAssignment(Command):
    def __init__(self, manager: ClubManager, locker_id: int, member_id: int) -> None:
        self._manager = manager
        self._locker_id = locker_id
        self._member_id = member_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info(
            "[Command] Triggering locker assignment. Locker ID: %s to Member ID: %s",
            self._locker_id, self._member_id
        )
        return self._manager.assign_locker(
            locker_id=self._locker_id,
            member_id=self._member_id
        )


class ExecuteLockerRelease(Command):
    def __init__(self, manager: ClubManager, locker_id: int) -> None:
        self._manager = manager
        self._locker_id = locker_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering locker release for Locker ID: %s", self._locker_id)
        return self._manager.release_locker(locker_id=self._locker_id)


class ExecuteEquipmentAdding(Command):
    def __init__(self, manager: ClubManager, name: str, state: str, date_purchase: date) -> None:
        self._manager = manager
        self._name = name
        self._state = state
        self._date_purchase = date_purchase
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering equipment creation: %s", self._name)
        return self._manager.create_equipment(
            name=self._name,
            state=self._state,
            date_purchase=self._date_purchase
        )


class ExecuteEquipmentStateUpdate(Command):
    def __init__(self, manager: ClubManager, equipment_id: int, new_state: str) -> None:
        self._manager = manager
        self._equipment_id = equipment_id
        self._new_state = new_state
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info(
            "[Command] Triggering state update for Equipment ID: %s to state: %s",
            self._equipment_id, self._new_state
        )
        return self._manager.update_equipment_state(
            equipment_id=self._equipment_id,
            new_state=self._new_state
        )


class ExecuteEquipmentDeletion(Command):
    def __init__(self, manager: ClubManager, equipment_id: int) -> None:
        self._manager = manager
        self._equipment_id = equipment_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering equipment deletion for ID: %s", self._equipment_id)
        return self._manager.delete_equipment(equipment_id=self._equipment_id)


class ExecuteLockerCreation(Command):
    def __init__(self, manager: ClubManager, locker_number: str) -> None:
        self._manager = manager
        self._locker_number = locker_number
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering locker creation with number: %s", self._locker_number)
        return self._manager.create_locker(locker_number=self._locker_number)

class ExecuteLockerDeletion(Command):
    def __init__(self, manager: ClubManager, locker_id: int) -> None:
        self._manager = manager
        self._locker_id = locker_id
        self._logger = AppLogger.get_instance()

    def execute(self) -> bool:
        self._logger.log_info("[Command] Triggering locker deletion for ID: %s", self._locker_id)
        return self._manager.delete_locker(locker_id=self._locker_id)
