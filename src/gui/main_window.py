from datetime import datetime

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton, QTableWidget, \
    QHeaderView, QTableWidgetItem, QMessageBox, QLineEdit, QInputDialog

from services.commands import ExecuteLockerDeletion
from src.services.commands import ExecuteLockerCreation
from src.database.orm_models import LockerORM, EquipmentORM
from src.gui.dialogs.change_equipment_state import ChangeEquipmentStateDialog
from src.gui.dialogs.create_equipment import CreateEquipmentDialog
from src.services.commands import ExecuteLockerAssignment, ExecuteLockerRelease, ExecuteEquipmentDeletion
from src.services.commands import ExecuteTrainerDeletion
from src.services.commands import ExecuteScheduleDeletion
from src.services.commands import ExecuteTrainingDeletion
from src.database.connection import DatabaseConnection
from src.database.orm_models import MemberORM, TrainerORM, ScheduleORM, VisitORM, TrainingORM
from src.gui.dialogs.create_schedule import CreateScheduleDialog
from src.gui.dialogs.create_training import CreateTrainingDialog
from src.gui.dialogs.member_edit import MemberFormDialog
from src.gui.dialogs.sell_subscription import SellSubscriptionDialog
from src.gui.dialogs.trainer_edit import TrainerFormDialog
from src.services.club_manager import ClubManager
from src.services.commands import ExecuteSubscriptionCancellation, ExecuteBookingCancellation
from src.services.commands import ExecuteTrainingBooking, ExecuteMemberDeletion
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
        self._init_booking_tab()
        self._init_schedule_tab()
        self._init_trainers_tab()
        self._init_lockers_and_inventory_tab()
        self._init_analytics_tab()

        self._logger.log_info("[GUI] Main window initialized successfully")

    def _init_members_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        action_bar_layout = QHBoxLayout()

        self.btn_register_member = QPushButton("Register Member")
        self.btn_edit_member = QPushButton("Edit Member Profile")
        self.btn_delete_member = QPushButton("Delete Member")
        self.btn_manage_sub = QPushButton("Manage subscription")
        self.btn_cancel_sub = QPushButton("Cancel subscription")
        self.btn_refresh_member_tab = QPushButton("Refresh")

        self.btn_delete_member.setStyleSheet("color: red")
        self.btn_edit_member.setStyleSheet("color: green")
        self.btn_register_member.setStyleSheet("color: green")
        self.btn_manage_sub.setStyleSheet("color: green")
        self.btn_cancel_sub.setStyleSheet("color: red")

        action_bar_layout.addWidget(self.btn_refresh_member_tab)
        action_bar_layout.addSpacing(30)
        action_bar_layout.addWidget(self.btn_register_member)
        action_bar_layout.addWidget(self.btn_edit_member)
        action_bar_layout.addWidget(self.btn_delete_member)
        action_bar_layout.addSpacing(30)
        action_bar_layout.addWidget(self.btn_manage_sub)
        action_bar_layout.addWidget(self.btn_cancel_sub)
        action_bar_layout.addStretch()

        main_layout.addLayout(action_bar_layout)

        filter_layout = QHBoxLayout()
        self.edit_search = QLineEdit()
        self.edit_search.setPlaceholderText("Quick search by name or phone number...")
        self.edit_search.setStyleSheet("padding: 5px; font-size: 14px")
        filter_layout.addWidget(self.edit_search)

        main_layout.addLayout(filter_layout)

        self.member_table = QTableWidget()
        self.member_table.setColumnCount(6)
        self.member_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Birth Date", "Phone", "Subscription type", "Valid until"])
        self.member_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.member_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.member_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        self.member_table.setAlternatingRowColors(True)
        self.member_table.verticalHeader().setVisible(False)

        main_layout.addWidget(self.member_table)

        self.btn_refresh_member_tab.clicked.connect(self.on_refresh_members_tab_button_click)
        self.btn_register_member.clicked.connect(self.on_register_member_button_click)
        self.btn_delete_member.clicked.connect(self.on_delete_member_button_click)
        self.btn_manage_sub.clicked.connect(self.on_sell_subscription_button_click)
        self.edit_search.textChanged.connect(self.on_member_search_text_changed)
        self.btn_edit_member.clicked.connect(self.on_edit_member_button_click)
        self.btn_cancel_sub.clicked.connect(self.on_cancel_sub_button_click)

        self.tabs.addTab(tab, "Members")
        self.load_members_from_db()

    def on_refresh_members_tab_button_click(self) -> None:
        self.load_members_from_db(target_table=self.member_table)

    def on_cancel_sub_button_click(self) -> None:
        current_row = self.member_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Please, select a member from table.")
            return

        member_id = int(self.member_table.item(current_row, 0).text())
        member_name = self.member_table.item(current_row, 1).text()
        sub_type = self.member_table.item(current_row, 4).text()

        if sub_type == "No Subscription" or "":
            QMessageBox.warning(self, "Warning", "Member doesn't have a subscription.")
            return

        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Are you sure you want to cancel member '{member_name}' subscription?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            command = ExecuteSubscriptionCancellation(
                manager=self._manager,
                member_id=member_id
            )

            if command.execute():
                QMessageBox.information(self, "Success", "Member subscription canceled.")
                self.on_refresh_members_tab_button_click()

            else:
                QMessageBox.critical(self, "Error", "Failed to cancel member subscription.")

    def on_delete_member_button_click(self) -> None:
        current_row = self.member_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Please, select a member from table to delete.")

        member_id = int(self.member_table.item(current_row, 0).text())
        member_name = self.member_table.item(current_row, 1).text()

        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Are you sure you want to delete member '{member_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            deletion_command = ExecuteMemberDeletion(manager=self._manager, member_id=member_id)

            if deletion_command.execute():
                QMessageBox.information(self, "Success",
                                        f"Member '{member_name}' was successfully deleted from the database.")
                self.on_refresh_members_tab_button_click()

            else:
                QMessageBox.critical(self, "Error", f"Database transaction failed. Unable to delete selected member.")

    def on_sell_subscription_button_click(self):
        current_row = self.member_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please, select a member")
            return

        member_id = int(self.member_table.item(current_row, 0).text())
        member_name = self.member_table.item(current_row, 1).text()

        dialog = SellSubscriptionDialog(
            member_id=member_id,
            member_name=member_name,
            parent=self
        )

        if dialog.exec():
            self.on_refresh_members_tab_button_click()

    def on_register_member_button_click(self):
        dialog = MemberFormDialog(parent=self)
        if dialog.exec():
            self.load_members_from_db()

    def on_edit_member_button_click(self):
        current_row = self.member_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please, select a member")
            return

        member_id = int(self.member_table.item(current_row, 0).text())
        current_name = self.member_table.item(current_row, 1).text()
        date_str = self.member_table.item(current_row, 2).text()
        current_phone = self.member_table.item(current_row, 3).text()

        current_birth_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        dialog = MemberFormDialog(
            member_id=member_id,
            current_name=current_name,
            current_phone=current_phone,
            current_birth_date=current_birth_date,
            parent=self
        )

        if dialog.exec():
            self.on_refresh_members_tab_button_click()

    def on_member_search_text_changed(self, search_text: str) -> None:
        search_text = search_text.strip().lower()

        for row in range(self.member_table.rowCount()):
            item_name = self.member_table.item(row, 1)
            item_phone = self.member_table.item(row, 3)

            name_text = item_name.text().lower() if item_name else ""
            phone_text = item_phone.text().lower() if item_phone else ""

            if not search_text or search_text in name_text or search_text in phone_text:
                self.member_table.setRowHidden(row, False)
            else:
                self.member_table.setRowHidden(row, True)

        self._logger.log_info("[GUI] Real-time search rendered for %s", search_text)

    def _init_trainers_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        button_layout = QHBoxLayout()
        self.btn_refresh_trainers = QPushButton("Refresh")
        self.btn_register_trainer = QPushButton("Register Trainer")
        self.btn_remove_trainer = QPushButton("Remove Trainer")
        self.btn_edit_trainer = QPushButton("Edit Trainer")

        button_layout.addWidget(self.btn_refresh_trainers)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.btn_register_trainer)
        button_layout.addWidget(self.btn_edit_trainer)
        button_layout.addWidget(self.btn_remove_trainer)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.btn_remove_trainer.setStyleSheet("color: red")
        self.btn_register_trainer.setStyleSheet("color: green")
        self.btn_edit_trainer.setStyleSheet("color: green")

        self.trainer_table = QTableWidget()
        self.trainer_table.setColumnCount(5)
        self.trainer_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Phone", "Speciality", "Experience"])
        self.trainer_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trainer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.trainer_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        main_layout.addWidget(self.trainer_table)

        self.trainer_table.verticalHeader().setVisible(False)
        self.trainer_table.setAlternatingRowColors(True)

        self.btn_refresh_trainers.clicked.connect(self.on_refresh_members_tab_button_click)
        self.btn_register_trainer.clicked.connect(self.on_register_trainer_button_click)
        self.btn_remove_trainer.clicked.connect(self.on_remove_trainer_button_click)
        self.btn_edit_trainer.clicked.connect(self.on_edit_trainer_button_click)

        self.tabs.addTab(tab, "Trainers")

        self.load_trainers_from_db()

    def on_edit_trainer_button_click(self):
        current_row = self.trainer_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please, select a trainer from the table to edit.")
            return

        trainer_id = int(self.trainer_table.item(current_row, 0).text())
        current_name = self.trainer_table.item(current_row, 1).text()
        current_phone = self.trainer_table.item(current_row, 2).text()
        current_speciality = self.trainer_table.item(current_row, 3).text()
        current_experience = self.trainer_table.item(current_row, 4).text()

        dialog = TrainerFormDialog(
            trainer_id=trainer_id,
            current_name=current_name,
            current_phone=current_phone,
            current_speciality=current_speciality,
            current_experience=current_experience,
            parent=self
        )

        if dialog.exec():
            self.load_trainers_from_db()
            self.on_schedule_refresh_button_click()

    def on_remove_trainer_button_click(self):
        current_row = self.trainer_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Please, select a trainer from the table to delete.")
            return

        trainer_id = int(self.trainer_table.item(current_row, 0).text())
        trainer_name = self.trainer_table.item(current_row, 1).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Trainer Deletion",
            f"Are you sure you want to remove trainer '{trainer_name}'?\n"
            "This will automatically remove all scheduled sessions for this trainer!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            deletion_command = ExecuteTrainerDeletion(manager=self._manager, trainer_id=trainer_id)

            if deletion_command.execute():
                QMessageBox.information(
                    self,
                    "Success",
                    f"Trainer '{trainer_name}' was successfully removed from the system."
                )
                self.load_trainers_from_db()
                self.on_schedule_refresh_button_click()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete trainer. Database layer error."
                )

    def _init_schedule_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)


        button_layout = QHBoxLayout()
        self.btn_add_training_type = QPushButton("Add Training Type")
        self.btn_remove_training = QPushButton("Remove Training")
        self.btn_add_to_schedule = QPushButton("Add To Schedule")
        self.btn_remove_schedule = QPushButton("Remove Schedule")
        self.btn_refresh_schedule = QPushButton("Refresh")

        button_layout.addWidget(self.btn_refresh_schedule)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.btn_add_training_type)
        button_layout.addWidget(self.btn_remove_training)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.btn_add_to_schedule)
        button_layout.addWidget(self.btn_remove_schedule)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.btn_remove_training.setStyleSheet("color: red")
        self.btn_remove_schedule.setStyleSheet("color: red")
        self.btn_add_to_schedule.setStyleSheet("color: green")
        self.btn_add_training_type.setStyleSheet("color: green")

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

        self.training_table.setAlternatingRowColors(True)
        self.training_table.verticalHeader().setVisible(False)

        self.trainers_schedule_table = QTableWidget()
        self.trainers_schedule_table.setColumnCount(5)
        self.trainers_schedule_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Phone", "Speciality", "Experience"])
        self.trainers_schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.trainers_schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.trainers_schedule_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        self.trainers_schedule_table.verticalHeader().setVisible(False)
        self.trainers_schedule_table.setAlternatingRowColors(True)

        self.schedule_table = QTableWidget()
        self.schedule_table.setColumnCount(5)
        self.schedule_table.setHorizontalHeaderLabels(
            ["Schedule ID", "Date", "Training name", "Trainer", "Available Slots"]
        )
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.schedule_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.schedule_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.schedule_table.verticalHeader().setVisible(False)
        self.schedule_table.setAlternatingRowColors(True)

        left_side_layout.addWidget(self.training_table)
        left_side_layout.addWidget(self.trainers_schedule_table)
        tables_layout.addLayout(left_side_layout)
        tables_layout.addWidget(self.schedule_table)

        main_layout.addLayout(tables_layout)

        self.btn_add_to_schedule.clicked.connect(self.on_add_to_schedule_button_click)
        self.btn_add_training_type.clicked.connect(self.on_add_training_type_button_click)
        self.btn_refresh_schedule.clicked.connect(self.on_schedule_refresh_button_click)
        self.btn_remove_training.clicked.connect(self.on_remove_training_button_click)
        self.btn_remove_schedule.clicked.connect(self.on_remove_schedule_button_click)

        self.tabs.addTab(tab, "Schedule")
        self.on_schedule_refresh_button_click()

    def on_remove_schedule_button_click(self) -> None:
        current_row = self.schedule_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Please, select a session from the Schedule table on the right to delete.")
            return

        schedule_id = int(self.schedule_table.item(current_row, 0).text())
        session_date = self.schedule_table.item(current_row, 1).text()
        training_name = self.schedule_table.item(current_row, 2).text()
        trainer_name = self.schedule_table.item(current_row, 3).text()

        confirm = QMessageBox.question(
            self,
            "Confirm Schedule Deletion",
            f"Are you sure you want to remove the session '{training_name}' ({session_date}) led by {trainer_name}?\n"
            "This will automatically cancel all client bookings for this specific session!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            deletion_command = ExecuteScheduleDeletion(manager=self._manager, schedule_id=schedule_id)

            if deletion_command.execute():
                QMessageBox.information(
                    self,
                    "Success",
                    f"Session '{training_name}' was successfully removed from the schedule."
                )
                self.on_schedule_refresh_button_click()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete schedule entry. Database layer error."
                )


    def on_remove_training_button_click(self):
        current_row = self.training_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Select training in the table first.")
            return

        training_id = int(self.training_table.item(current_row, 0).text())

        confirm = QMessageBox.question(
            self,
            "Confirmation",
            "Are you sure you want to remove training?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            command = ExecuteTrainingDeletion(manager=self._manager, training_id=training_id)

            if command.execute():
                QMessageBox.information(self, "Success", "Training has been removed.")
            self.on_schedule_refresh_button_click()

        else:
            QMessageBox.critical(self, "Warning", "Failed to remove training.")

    def on_add_training_type_button_click(self):
        dialog = CreateTrainingDialog(parent=self)
        dialog.exec()
        self.on_schedule_refresh_button_click()

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
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        button_layout = QHBoxLayout()
        self.btn_refresh_lockers_and_inventory_tab = QPushButton("Refresh")
        self.btn_delete_locker = QPushButton("Delete Locker")
        self.btn_add_locker = QPushButton("Add Locker")
        self.btn_assign_locker = QPushButton("Assign Locker to Member")
        self.btn_release_locker = QPushButton("Free Locker")
        self.btn_add_equipment = QPushButton("Add Equipment")
        self.btn_change_equipment_state = QPushButton("Change Equipment State")
        self.btn_delete_equipment = QPushButton("Delete Equipment")

        button_layout.addWidget(self.btn_refresh_lockers_and_inventory_tab)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.btn_add_locker)
        button_layout.addWidget(self.btn_delete_locker)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.btn_assign_locker)
        button_layout.addWidget(self.btn_release_locker)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.btn_add_equipment)
        button_layout.addWidget(self.btn_change_equipment_state)
        button_layout.addWidget(self.btn_delete_equipment)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

        self.btn_assign_locker.setStyleSheet("color: green")
        self.btn_delete_locker.setStyleSheet("color: red")
        self.btn_add_locker.setStyleSheet("color: green")
        self.btn_release_locker.setStyleSheet("color: red")
        self.btn_add_equipment.setStyleSheet("color: green")
        self.btn_change_equipment_state.setStyleSheet("color: orange")
        self.btn_delete_equipment.setStyleSheet("color: red")

        tables_layout = QHBoxLayout()

        self.locker_table = QTableWidget()
        self.locker_table.setColumnCount(4)
        self.locker_table.setHorizontalHeaderLabels(["Locker ID", "Number", "Status", "Occupied By (Member ID)"])
        self.locker_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.locker_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.locker_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.locker_table.setAlternatingRowColors(True)
        self.locker_table.verticalHeader().setVisible(False)
        tables_layout.addWidget(self.locker_table)

        self.eq_table = QTableWidget()
        self.eq_table.setColumnCount(4)
        self.eq_table.setHorizontalHeaderLabels(["Asset ID", "Name", "Technical State", "Purchase Date"])
        self.eq_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.eq_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.eq_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.eq_table.setAlternatingRowColors(True)
        self.eq_table.verticalHeader().setVisible(False)
        tables_layout.addWidget(self.eq_table)

        main_layout.addLayout(tables_layout)

        self.btn_refresh_lockers_and_inventory_tab.clicked.connect(self.on_refresh_lockers_and_inventory_button_click)
        self.btn_assign_locker.clicked.connect(self.on_assign_locker_button_click)
        self.btn_release_locker.clicked.connect(self.on_release_locker_button_click)
        self.btn_add_equipment.clicked.connect(self.on_add_equipment_button_click)
        self.btn_change_equipment_state.clicked.connect(self.on_change_equipment_state_button_click)
        self.btn_delete_equipment.clicked.connect(self.on_delete_equipment_button_click)
        self.btn_add_locker.clicked.connect(self.on_add_locker_button_click)
        self.btn_delete_locker.clicked.connect(self.on_delete_locker_button_click)

        self.tabs.addTab(tab, "Lockers and Inventory")

        self.on_refresh_lockers_and_inventory_button_click()

    def on_delete_locker_button_click(self) -> None:
        current_row = self.locker_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Please, select a locker from the table first.")
            return

        locker_id = int(self.locker_table.item(current_row, 0).text())
        locker_number = self.locker_table.item(current_row, 1).text()
        status = self.locker_table.item(current_row, 2).text()

        warning_extra = ""
        if status == "Occupied":
            warning_extra = "\nWARNING: This locker is currently occupied by a member!"

        confirm = QMessageBox.question(
            self,
            "Confirm Locker Deletion",
            f"Are you sure you want to permanently delete locker #{locker_number}?{warning_extra}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            command = ExecuteLockerDeletion(self._manager, locker_id)

            if command.execute():
                QMessageBox.information(
                    self,
                    "Success",
                    f"Locker #{locker_number} was successfully removed from the database."
                )
                self.load_lockers_from_db()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete locker from the database layer."
                )


    def on_add_locker_button_click(self):
        locker_number, ok = QInputDialog.getText(
            self,
            "New Locker",
            "Enter Unique Locker Number or Label (e.g. 42A):"
        )

        if ok and locker_number.strip():
            command = ExecuteLockerCreation(self._manager, locker_number)

            if command.execute():
                QMessageBox.information(
                    self,
                    "Success",
                    f"Locker #{locker_number} successfully registered in the system."
                )
                self.load_lockers_from_db()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create locker. A locker with number '{locker_number}' might already exist."
                )


    def load_lockers_from_db(self):
        session = self._db.open_session()
        try:
            lockers = session.query(LockerORM).all()
            self.locker_table.setRowCount(len(lockers))
            for row, locker in enumerate(lockers):
                self.locker_table.setItem(row, 0, QTableWidgetItem(str(locker.id)))
                self.locker_table.setItem(row, 1, QTableWidgetItem(str(locker.number)))
                self.locker_table.setItem(row, 2, QTableWidgetItem(str(locker.status)))

                member_text = str(locker.member_id) if locker.member_id else "-"
                self.locker_table.setItem(row, 3, QTableWidgetItem(member_text))
            self._logger.log_info("[GUI] Loaded %d club lockers from database" % len(lockers))
        except Exception as e:
            self._logger.log_error("[GUI] Failed to load lockers: %s" % e)
        finally:
            self._db.close_session(session, status=True)

    def load_equipment_from_db(self):
        session = self._db.open_session()
        try:
            equipment_list = session.query(EquipmentORM).all()
            self.eq_table.setRowCount(len(equipment_list))
            for row, eq in enumerate(equipment_list):
                self.eq_table.setItem(row, 0, QTableWidgetItem(str(eq.id)))
                self.eq_table.setItem(row, 1, QTableWidgetItem(str(eq.name)))
                self.eq_table.setItem(row, 2, QTableWidgetItem(str(eq.state)))

                date_str = eq.date_purchase.strftime("%d.%m.%Y") if eq.date_purchase else "-"
                self.eq_table.setItem(row, 3, QTableWidgetItem(date_str))
            self._logger.log_info("[GUI] Loaded %d equipment assets from database" % len(equipment_list))
        except Exception as e:
            self._logger.log_error("[GUI] Failed to load equipment: %s" % e)
        finally:
            self._db.close_session(session, status=True)


    def on_assign_locker_button_click(self):
        current_row = self.locker_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Select a locker to assign.")
            return

        locker_id = int(self.locker_table.item(current_row, 0).text())
        status = self.locker_table.item(current_row, 2).text()

        if status == "Occupied":
            QMessageBox.warning(self, "Error", "This locker is already occupied by another member.")
            return

        member_id, ok = QInputDialog.getInt(self, "Locker Assignment", "Enter Member ID to assign this locker:")
        if ok:
            command = ExecuteLockerAssignment(self._manager, locker_id, member_id)
            if command.execute():
                QMessageBox.information(self, "Success", f"Locker assigned successfully to Member ID {member_id}.")
                self.load_lockers_from_db()
            else:
                QMessageBox.critical(self, "Error", "Failed to assign locker. Ensure the member exists and doesn't already have a locker.")

    def on_release_locker_button_click(self):
        current_row = self.locker_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Select a locker to release.")
            return

        locker_id = int(self.locker_table.item(current_row, 0).text())
        status = self.locker_table.item(current_row, 2).text()

        if status == "Available":
            QMessageBox.warning(self, "Warning", "This locker is already free.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Release", f"Are you sure you want to free up locker ID {locker_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            command = ExecuteLockerRelease(self._manager, locker_id)
            if command.execute():
                QMessageBox.information(self, "Success", "Locker is now available.")
                self.load_lockers_from_db()
            else:
                QMessageBox.critical(self, "Error", "Failed to release locker.")

    def on_add_equipment_button_click(self):
        dialog = CreateEquipmentDialog(parent=self)
        if dialog.exec():
            self.load_equipment_from_db()

    def on_change_equipment_state_button_click(self):
        current_row = self.eq_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Select an equipment to change.")
            return

        eq_id = int(self.eq_table.item(current_row, 0).text())
        name = self.eq_table.item(current_row, 1).text()
        state = self.eq_table.item(current_row, 2).text()

        dialog = ChangeEquipmentStateDialog(eq_id, name, state, parent=self)
        if dialog.exec():
            self.load_equipment_from_db()

    def on_delete_equipment_button_click(self):
        current_row = self.eq_table.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "Warning", "Select an equipment item to decommission.")
            return

        eq_id = int(self.eq_table.item(current_row, 0).text())
        name = self.eq_table.item(current_row, 1).text()

        confirm = QMessageBox.question(
            self, "Confirm Write-off", f"Are you sure you want to decommission and permanently delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            command = ExecuteEquipmentDeletion(self._manager, eq_id)
            if command.execute():
                QMessageBox.information(self, "Success", f"Asset '{name}' was written off successfully.")
                self.eq_table.removeRow(current_row)
            else:
                QMessageBox.critical(self, "Error", "Failed to decommission equipment.")



    def on_refresh_lockers_and_inventory_button_click(self):
        self.load_lockers_from_db()
        self.load_equipment_from_db()


    def _init_booking_tab(self):
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        button_layout = QHBoxLayout()
        self.btn_book_training = QPushButton("Book Training")
        self.btn_refresh_booking_tab = QPushButton("Refresh")
        self.btn_cancel_booking = QPushButton("Cancel Booking")

        self.btn_book_training.setStyleSheet("color: green")
        self.btn_cancel_booking.setStyleSheet("color: red")

        button_layout.addWidget(self.btn_refresh_booking_tab)
        button_layout.addSpacing(30)
        button_layout.addWidget(self.btn_book_training)
        button_layout.addWidget(self.btn_cancel_booking)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

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

        self.booking_member_table.setAlternatingRowColors(True)
        self.booking_member_table.verticalHeader().setVisible(False)

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

        self.booking_schedule_table.setAlternatingRowColors(True)
        self.booking_schedule_table.verticalHeader().setVisible(False)

        self.visit_table = QTableWidget()
        self.visit_table.setColumnCount(5)
        self.visit_table.setHorizontalHeaderLabels(
            ["Visit ID", "Training Date", "Member Name", "Training Name", "Status"]
        )
        self.visit_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.visit_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.visit_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.visit_table.setAlternatingRowColors(True)
        self.visit_table.verticalHeader().setVisible(False)

        main_layout.addLayout(top_tables_layout)
        main_layout.addWidget(self.visit_table)

        self.btn_book_training.clicked.connect(self.on_book_training_button_click)
        self.btn_refresh_booking_tab.clicked.connect(self.on_refresh_booking_tab_button_click)
        self.btn_cancel_booking.clicked.connect(self.on_cancel_booking_button_click)

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

    def on_cancel_booking_button_click(self):
        current_row = self.visit_table.currentRow()

        if current_row == -1:
            QMessageBox.warning(self, "Error", "Please select member in table first")
            return

        visit_id = int(self.visit_table.item(current_row, 0).text())
        member_name = self.visit_table.item(current_row, 2).text()
        training_name = self.visit_table.item(current_row, 3).text()

        confirm = QMessageBox.question(
            self,
            "Confirmation",
            f"Are you sure you want to cancel booking {member_name} for {training_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            command = ExecuteBookingCancellation(manager=self._manager, visit_id=visit_id)

            if command.execute():
                QMessageBox.information(
                    self,
                    "Success",
                    "Booking was successfully cancelled."
                )
                self.on_refresh_booking_tab_button_click()

            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to cancel booking."
                )

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

    def on_register_trainer_button_click(self):
        dialog = TrainerFormDialog(parent=self)
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
