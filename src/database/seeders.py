from datetime import date

from src.database.connection import DatabaseConnection
from src.database.orm_models import MemberORM
from src.utils.logger import AppLogger


def seed_initial_data() -> None:
    _logger = AppLogger.get_instance()
    _db = DatabaseConnection.get_instance()
    _session = _db.open_session()
    status = False

    if _session.query(MemberORM).count() == 0:
        _logger.log_info("[Database.Seeder] Table 'Members' is empty. Adding demo records...")

        member_1 = MemberORM(
            full_name="Иван Иванов",
            birth_date=date(1995, 4, 12),
            phone="89991112233"
        )
        member_2 = MemberORM(
            full_name="Мария Сидорова",
            birth_date=date(2001, 8, 24),
            phone="89005553535"
        )




        _session.add_all([member_1, member_2])
        status = True
        _db.close_session(_session, status)