from datetime import date

from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class MemberORM(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)

    subscription_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=True, init=False
    )

    visit_entries: Mapped[list[VisitORM]] = relationship(
        "VisitORM",
        back_populates="member",
        cascade="all, delete-orphan",
        init=False
    )
    locker: Mapped[LockerORM | None] = relationship(
        "LockerORM",
        back_populates="member",
        uselist=False,
        init=False
    )
    subscription: Mapped[SubscriptionORM | None] = relationship(
        "SubscriptionORM",
        back_populates="member",
        uselist=False,
        init=False
    )
    payments: Mapped[list[PaymentORM]] = relationship(
        "PaymentORM",
        back_populates="member",
        cascade="all, delete-orphan",
        init=False
    )
    reviews: Mapped[list[ReviewORM]] = relationship(
        "ReviewORM",
        back_populates="member",
        cascade="all, delete-orphan",
        init=False
    )


class TrainerORM(Base):
    __tablename__ = "trainers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    experience: Mapped[str] = mapped_column(String(100), nullable=False)

    schedule_entries: Mapped[list[ScheduleORM]] = relationship(
        "ScheduleORM",
        back_populates="trainer",
        cascade="all, delete-orphan",
        init=False
    )


class TrainingORM(Base):
    __tablename__ = "trainings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    schedule_entries: Mapped[list[ScheduleORM]] = relationship(
        "ScheduleORM",
        back_populates="training",
        cascade="all, delete-orphan",
        init=False
    )
    visit_entries: Mapped[list[VisitORM]] = relationship(
        "VisitORM",
        back_populates="training",
        cascade="all, delete-orphan",
        init=False
    )


class ScheduleORM(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)

    trainer_id: Mapped[int] = mapped_column(Integer, ForeignKey("trainers.id", ondelete="CASCADE"), nullable=False)
    training_id: Mapped[int] = mapped_column(Integer, ForeignKey("trainings.id", ondelete="CASCADE"), nullable=False)

    trainer: Mapped[TrainerORM] = relationship("TrainerORM", back_populates="schedule_entries", init=False)
    training: Mapped[TrainingORM] = relationship("TrainingORM", back_populates="schedule_entries", init=False)


class VisitORM(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    date: Mapped[Date] = mapped_column(Date, nullable=False)

    training_id: Mapped[int] = mapped_column(Integer, ForeignKey("trainings.id", ondelete="CASCADE"), nullable=False)
    member_id: Mapped[int] = mapped_column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)

    member: Mapped[MemberORM] = relationship("MemberORM", back_populates="visit_entries", init=False)
    training: Mapped[TrainingORM] = relationship("TrainingORM", back_populates="visit_entries", init=False)


class SubscriptionORM(Base):
    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)

    member: Mapped[MemberORM] = relationship("MemberORM", back_populates="subscription", uselist=False, init=False)
    payments: Mapped[list[PaymentORM]] = relationship("PaymentORM", back_populates="subscription", init=False)


class PaymentORM(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)

    member_id: Mapped[int] = mapped_column(Integer, ForeignKey("members.id", ondelete="CASCADE"), nullable=False)
    subscription_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("subscriptions.id", ondelete="CASCADE"),
        nullable=False
    )

    member: Mapped[MemberORM] = relationship("MemberORM", back_populates="payments", init=False)
    subscription: Mapped[SubscriptionORM] = relationship("SubscriptionORM", back_populates="payments", init=False)


class LockerORM(Base):
    __tablename__ = "lockers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    number: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False)

    member_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("members.id", ondelete="SET NULL"), nullable=True,
                                                  unique=True)

    member: Mapped[MemberORM | None] = relationship("MemberORM", back_populates="locker", init=False)


class EquipmentORM(Base):
    __tablename__ = "equipments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, init=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    date_purchase: Mapped[date] = mapped_column(Date, nullable=False)


class ReviewORM(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mark: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)

    member_id: Mapped[int] = mapped_column(Integer, ForeignKey("members.id"), nullable=False)
    member: Mapped[MemberORM] = relationship("MemberORM", back_populates="reviews")
