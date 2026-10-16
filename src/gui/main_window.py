from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton, QTableWidget, \
    QHeaderView, QTableWidgetItem, QMessageBox

from src.database.connection import DatabaseConnection
from src.database.orm_models import MemberORM, TrainerORM, ScheduleORM, VisitORM, TrainingORM
from src.gui.dialogs.create_schedule import CreateScheduleDialog
from src.gui.dialogs.create_training import CreateTrainingDialog
from src.gui.dialogs.member_registration import MemberRegistrationDialog
from src.gui.dialogs.trainer_registration import TrainerRegistrationDialog
from src.services.club_manager import ClubManager
from src.services.commands import ExecuteSubscriptionSale, ExecuteTrainingBooking
from src.utils.logger import AppLogger


class FitnessClubMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._logger = AppLogger.get_instance()
        self._db = DatabaseConnection.get_instance()
        self._manager = ClubManager()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.central_widget.setWindowTitle("Fitness Club Manager")
        self.central_widget.setMinimumSize(QSize(1280, 800))

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self._init_members_tab()
        self._init_trainers_tab()
        self._init_schedule_tab()
        self._init_lockers_and_inventory_tab()
        self._init_analytics_tab()
        self._init_booking_tab()

        self._logger.log_info("[GUI] Main window initialized successfully")

    def _init_members_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        button_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_sell_sub = QPushButton("Sell subscription")
        self.btn_register_member = QPushButton("Register Member")

        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.btn_sell_sub)
        button_layout.addWidget(self.btn_register_member)
        layout.addLayout(button_layout)

        self.member_table = QTableWidget()
        self.member_table.setColumnCount(6)
        self.member_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Birth Date", "Phone", "Subscription type", "Valid until"])
        self.member_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.member_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.member_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.member_table)

        self.btn_refresh.clicked.connect(self.load_members_from_db)
        self.btn_sell_sub.clicked.connect(self.on_sell_subscription_button_click)
        self.btn_register_member.clicked.connect(self.on_register_member_button_click)

        self.tabs.addTab(tab, "Reception and Clients")

        self.load_members_from_db()

    def _init_trainers_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        button_layout = QHBoxLayout()
        self.btn_refresh_trainers = QPushButton("Refresh")
        self.btn_register_trainer = QPushButton("Register Trainer")

        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.btn_register_trainer)
        layout.addLayout(button_layout)

        self.trainer_table = QTableWidget()
        self.trainer_table.setColumnCount(5)
        self.trainer_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Phone", "Speciality", "Experience"])
        self.trainer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trainer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.trainer_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.trainer_table)

        self.btn_refresh_trainers.clicked.connect(self.load_trainers_from_db)
        self.btn_register_trainer.clicked.connect(self.on_register_trainer_button_click)

        self.tabs.addTab(tab, "Trainers")

        self.load_trainers_from_db()

    def _init_schedule_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        button_layout = QHBoxLayout()
        self.btn_add_training_type = QPushButton("Add Training Type")
        self.btn_add_to_schedule = QPushButton("Add To Schedule")
        self.btn_refresh_schedule = QPushButton("Refresh")

        button_layout.addWidget(self.btn_add_training_type)
        button_layout.addWidget(self.btn_add_to_schedule)
        button_layout.addWidget(self.btn_refresh_schedule)
        layout.addLayout(button_layout)

        tables_layout = QHBoxLayout()
        left_side_layout = QVBoxLayout()

        self.training_table = QTableWidget()
        self.training_table.setColumnCount(4)
        self.training_table.setHorizontalHeaderLabels(
            ["Training ID", "Training name", "Training type", "Duration"]
        )
        self.training_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.training_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.training_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.trainers_schedule_table = QTableWidget()
        self.trainers_schedule_table.setColumnCount(5)
        self.trainers_schedule_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Phone", "Speciality", "Experience"])
        self.trainers_schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trainers_schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.trainers_schedule_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels(
            ["Schedule ID", "Date", "Training name", "Trainer", "Available Slots"]
        )
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        left_side_layout.addWidget(self.training_table)
        left_side_layout.addWidget(self.trainers_schedule_table)
        tables_layout.addLayout(left_side_layout)
        tables_layout.addWidget(self.schedule_table)

        layout.addLayout(tables_layout)

        self.btn_add_to_schedule.clicked.connect(self.on_add_to_schedule_button_click)
        self.btn_add_training_type.clicked.connect(self.on_add_training_type_button_click)
        self.btn_refresh_schedule.clicked.connect(self.on_schedule_refresh_button_click)

        self.tabs.addTab(tab, "Schedule")
        self.on_schedule_refresh_button_click()

    def on_add_training_type_button_click(self):
        dialog = CreateTrainingDialog(parent=self)
        dialog.exec()

    def on_add_to_schedule_button_click(self):
        training_id = None
        selected_training_row = self.training_table.currentRow()
        if selected_training_row != -1:
            training_id = int(self.training_table.item(selected_training_row, 0).text())

        trainer_id = None
        selected_trainer_row = self.trainers_schedule_table.currentRow()
        if selected_trainer_row != -1:
            trainer_id = int(self.trainers_schedule_table.item(selected_trainer_row, 0).text())

        dialog = CreateScheduleDialog(trainer_id=trainer_id, training_id=training_id, parent=self)
        if dialog.exec():
            self.load_schedule_from_db()

    def _init_lockers_and_inventory_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addLayout(layout)
        self.tabs.addTab(tab, "Lockers and Inventory")

    def _init_booking_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        button_layout = QHBoxLayout()
        self.btn_book_training = QPushButton("Book Training")
        self.btn_refresh_booking_tab = QPushButton("Refresh")

        button_layout.addWidget(self.btn_book_training)
        button_layout.addWidget(self.btn_refresh_booking_tab)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        top_tables_layout = QHBoxLayout()

        self.booking_member_table = QTableWidget()
        self.booking_member_table.setColumnCount(6)
        self.booking_member_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Birth Date", "Phone", "Subscription type", "Valid until"]
        )
        self.booking_member_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.booking_member_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.booking_member_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.booking_member_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.booking_member_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        top_tables_layout.addWidget(self.booking_member_table)

        self.booking_schedule_table = QTableWidget()
        self.booking_schedule_table.setColumnCount(5)
        self.booking_schedule_table.setHorizontalHeaderLabels(
            ["Schedule ID", "Date", "Training name", "Trainer", "Available Slots"]
        )
        self.booking_schedule_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.booking_schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.booking_schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.booking_schedule_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.booking_schedule_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        top_tables_layout.addWidget(self.booking_schedule_table)

        self.visit_table = QTableWidget()
        self.visit_table.setColumnCount(5)
        self.visit_table.setHorizontalHeaderLabels(
            ["Visit ID", "Training Date", "Member Name", "Training Name", "Status"]
        )
        self.visit_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.visit_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.visit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        layout.addLayout(top_tables_layout)
        layout.addWidget(self.visit_table)

        self.btn_book_training.clicked.connect(self.on_book_training_button_click)
        self.btn_refresh_booking_tab.clicked.connect(self.on_refresh_booking_tab_button_click)

        self.tabs.addTab(tab, "Booking")
        self.on_refresh_booking_tab_button_click()

    def on_refresh_booking_tab_button_click(self):
        self.load_schedule_from_db(target_table=self.booking_schedule_table)
        self.load_members_from_db(target_table=self.booking_member_table)
        self.load_visits_from_db(target_table=self.visit_table)

    def on_book_training_button_click(self):
        current_member_row = self.booking_member_table.currentRow()
        current_schedule_row = self.booking_schedule_table.currentRow()

        if current_member_row == -1:
            QMessageBox.warning(self, "Error", "Please select member in table first")
            return

        if current_schedule_row == -1:
            QMessageBox.warning(self, "Error", "Please select schedule in table first")
            return

        member_id = int(self.booking_member_table.item(current_member_row, 0).text())
        member_name = self.booking_member_table.item(current_member_row, 1).text()
        schedule_id = int(self.booking_schedule_table.item(current_schedule_row, 0).text())
        training_name = self.booking_schedule_table.item(current_schedule_row, 2).text()

        booking_command = ExecuteTrainingBooking(
            manager=self._manager,
            member_id=member_id,
            schedule_id=schedule_id
        )

        if booking_command.execute():
            QMessageBox.information(self, "Success", f"Successfully booking {member_name} for {training_name}")

        self.on_refresh_booking_tab_button_click()

    def load_visits_from_db(self, target_table: QTableWidget | None = None) -> None:
        if target_table is None:
            target_table = self.visit_table

        session = self._db.open_session()
        try:
            all_visits = session.query(VisitORM).all()
            target_table.setRowCount(len(all_visits))

            for row, visit in enumerate(all_visits):
                target_table.setItem(row, 0, QTableWidgetItem(str(visit.id)))
                target_table.setItem(row, 1, QTableWidgetItem(visit.date.strftime("%d.%m.%Y")))
                target_table.setItem(row, 2, QTableWidgetItem(visit.member.full_name))
                target_table.setItem(row, 3, QTableWidgetItem(visit.training.name))
                target_table.setItem(row, 4, QTableWidgetItem("Active / Confirmed"))

            self._logger.log_info("[GUI] Loaded %d visits from database" % len(all_visits))

        except Exception as e:
            self._logger.log_error("[GUI] Failed to load visits from database: %s" % e)
            QMessageBox.warning(self, "Error", f"Failed to load visits from database: {e}")

        finally:
            self._db.close_session(session, status=True)


    def _init_analytics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addLayout(layout)
        self.tabs.addTab(tab, "Club Analytics")

    def load_members_from_db(self, target_table: QTableWidget | None = None) -> None:
        if target_table is None:
            target_table = self.member_table

        session = self._db.open_session()
        try:
            members = session.query(MemberORM).all()
            target_table.setRowCount(len(members))

            for row, member in enumerate(members):
                target_table.setItem(row, 0, QTableWidgetItem(str(member.id)))
                target_table.setItem(row, 1, QTableWidgetItem(str(member.full_name)))
                target_table.setItem(row, 2, QTableWidgetItem(str(member.birth_date)))
                target_table.setItem(row, 3, QTableWidgetItem(str(member.phone)))

                if member.subscription:
                    sub_type = str(member.subscription.type)
                    valid_until = member.subscription.end_date.strftime("%d.%m.%Y")
                else:
                    sub_type = "No subscription"
                    valid_until = "-"

                target_table.setItem(row, 4, QTableWidgetItem(sub_type))
                target_table.setItem(row, 5, QTableWidgetItem(valid_until))

            self._logger.log_info("[GUI] Loaded %d members from database" % len(members))

        except Exception as e:
            self._logger.log_error("[GUI] Failed to load members from database: %s" % e)
            QMessageBox.critical(self, "Error", f"Failed to load members from database: {e}")

        finally:
            self._db.close_session(session, status=True)

    def load_trainers_from_db(self, target_table: QTableWidget | None = None):
        if target_table is None:
            target_table = self.trainer_table

        session = self._db.open_session()
        try:
            trainers = session.query(TrainerORM).all()
            target_table.setRowCount(len(trainers))

            for row, trainer in enumerate(trainers):
                target_table.setItem(row, 0, QTableWidgetItem(str(trainer.id)))
                target_table.setItem(row, 1, QTableWidgetItem(str(trainer.full_name)))
                target_table.setItem(row, 2, QTableWidgetItem(str(trainer.phone)))
                target_table.setItem(row, 3, QTableWidgetItem(str(trainer.specialty)))
                target_table.setItem(row, 4, QTableWidgetItem(str(trainer.experience)))

            self._logger.log_info("[GUI] Loaded %d trainers from database" % len(trainers))

        except Exception as e:
            self._logger.log_error("[GUI] Failed to load trainers from database: %s" % e)
            QMessageBox.critical(self, "Error", f"Failed to load trainers from database: {e}")

        finally:
            self._db.close_session(session, status=True)

    def on_sell_subscription_button_click(self):
        current_row = self.member_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please, select a member")
            return

        member_id = int(self.member_table.item(current_row, 0).text())

        sale_command = ExecuteSubscriptionSale(
            manager=self._manager,
            member_id=member_id,
            subscription_type="monthly",
            payment_method="card",
            discount_type="student"
        )

        success = sale_command.execute()
        if success:
            self.load_members_from_db()

    def on_register_member_button_click(self):
        dialog = MemberRegistrationDialog(parent=self)
        if dialog.exec():
            self.load_members_from_db()

    def on_register_trainer_button_click(self):
        dialog = TrainerRegistrationDialog(parent=self)
        if dialog.exec():
            self.load_trainers_from_db()

    def load_schedule_from_db(self, target_table: QTableWidget | None = None):
        if target_table is None:
            target_table = self.schedule_table

        session = self._db.open_session()
        try:
            schedule_entries = session.query(ScheduleORM).all()
            target_table.setRowCount(len(schedule_entries))

            for row, entry in enumerate(schedule_entries):
                booked_slots = session.query(VisitORM).filter_by(
                    training_id=entry.training_id,
                    date=entry.date
                ).count()

                max_slots = 15
                slots_text = f"{booked_slots} / {max_slots}"

                target_table.setItem(row, 0, QTableWidgetItem(str(entry.id)))
                target_table.setItem(row, 1, QTableWidgetItem(entry.date.strftime("%d.%m.%Y")))
                target_table.setItem(row, 2, QTableWidgetItem(str(entry.training.name)))
                target_table.setItem(row, 3, QTableWidgetItem(str(entry.trainer.full_name)))
                target_table.setItem(row, 4, QTableWidgetItem(slots_text))

            self._logger.log_info("[GUI] Successfully loaded %d schedule entries from database" % len(schedule_entries))

        except Exception as e:
            self._logger.log_error("[GUI] Failed to load schedule from database: %s" % e)
            QMessageBox.critical(self, "Error", f"Failed to load schedule from database: {e}")

        finally:
            self._db.close_session(session, status=True)

    def load_trainings_from_db(self):
        session = self._db.open_session()
        try:
            trainings = session.query(TrainingORM).all()
            self.training_table.setRowCount(len(trainings))

            for row, training in enumerate(trainings):
                self.training_table.setItem(row, 0, QTableWidgetItem(str(training.id)))
                self.training_table.setItem(row, 1, QTableWidgetItem(str(training.name)))
                self.training_table.setItem(row, 2, QTableWidgetItem(str(training.type)))
                self.training_table.setItem(row, 3, QTableWidgetItem(f"{training.duration_minutes} min"))

            self._logger.log_info("[GUI] Successfully loaded %d trainings from database" % len(trainings))

        except Exception as e:
            self._logger.log_error("[GUI] Failed to load training from database: %s" % e)
            QMessageBox.critical(self, "Error", f"Failed to load training from database: {e}")

        finally:
            self._db.close_session(session, status=True)

    def on_schedule_refresh_button_click(self):
        self.load_schedule_from_db()
        self.load_trainings_from_db()
        self.load_trainers_from_db(target_table=self.trainers_schedule_table)
