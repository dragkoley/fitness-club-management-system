import unittest
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.services.commands import ExecuteSubscriptionSale
from src.database.connection import DatabaseConnection
from src.database.orm_models import MemberORM, SubscriptionORM, PaymentORM
from src.services.club_manager import ClubManager


class ClubManagerSubscriptionSaleTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.db = DatabaseConnection.get_instance()
        self.db.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        self.db.SessionFactory = sessionmaker(bind=self.db.engine)
        self.db.init_db()

        session = self.db.open_session()
        status = False
        try:
            self.test_member = MemberORM(
                full_name="Ivan Ivanov",
                birth_date=date(2000, 5, 15),
                phone="88005553535"
            )
            session.add(self.test_member)
            session.flush()
            self.member_id = self.test_member.id
            status = True

        except Exception as e:
            status = False
            raise
        finally:
            self.db.close_session(session, status)


    def test_sell_monthly_subscription_with_student_discount_via_card(self) -> None:
        manager = ClubManager()

        sale_command = ExecuteSubscriptionSale(
            manager=manager,
            member_id=self.member_id,
            subscription_type="monthly",
            payment_method="card",
            discount_type="student"
        )

        result: bool = sale_command.execute()

        # result: bool = manager.sell_subscription(
        #     self.member_id, subscription_type="monthly", payment_method="card", discount_type="student")

        self.assertTrue(result, "[Test] Transaction status must be True after selling the subscription")
        verification_session = self.db.open_session()
        v_status = False
        try:
            updated_member = verification_session.get(MemberORM, self.member_id)
            self.assertIsNotNone(updated_member.subscription_id, "[Test] Member must have subscription ID in profile")

            checked_subscription = verification_session.get(SubscriptionORM, updated_member.subscription_id)
            self.assertEqual(checked_subscription.price, 2400,
                             "[Test] Subscription price must be 2400 (3000 - 20% = 2400)")

            checked_receipt = verification_session.query(PaymentORM).filter_by(member_id=self.member_id).first()
            self.assertIsNotNone(checked_receipt, "[Test] Payment was created")
            self.assertEqual(checked_receipt.status, "Success", "[Test] Status must be Success")
            self.assertEqual(checked_receipt.type, "Card", "[Test] Type must be Card")

            v_status = True

        except Exception as e:
            raise

        finally:
            self.db.close_session(verification_session, v_status)


if __name__ == "__main__":
    unittest.main()
