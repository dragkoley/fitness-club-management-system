from datetime import date
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QLabel, QLineEdit, QMessageBox, QDateEdit, QSpinBox
from src.services.commands import ExecuteScheduleCreation
from src.services.club_manager import ClubManager
from src.gui.dialogs.base_dialog import BaseFormDialog

class CreateScheduleDialog(BaseFormDialog):
    def __init__(self, training_id: int | None = None, trainer_id: int | None = None, parent=None):
        self._manager = ClubManager()
        self._predefined_training_id = training_id
        self._predefined_trainer_id = trainer_id

        super().__init__(title="Add Training to Schedule", width=350, height=280, parent=parent)

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Date of Training:"))
        self.edit_date = QDateEdit()
        self.edit_date.setCalendarPopup(True)
        self.edit_date.setDate(QDate.currentDate())
        self.main_layout.addWidget(self.edit_date)

        self.main_layout.addWidget(QLabel("Trainer ID:"))
        self.spin_trainer_id = QSpinBox()
        self.spin_trainer_id.setRange(1, 99999)
        if self._predefined_trainer_id is not None:
            self.spin_trainer_id.setValue(self._predefined_trainer_id)
        self.main_layout.addWidget(self.spin_trainer_id)

        self.main_layout.addWidget(QLabel("Training Program ID:"))
        self.spin_training_id = QSpinBox()
        self.spin_training_id.setRange(1, 99999)
        if self._predefined_training_id is not None:
            self.spin_training_id.setValue(self._predefined_training_id)
        self.main_layout.addWidget(self.spin_training_id)

    def _on_confirm_clicked(self) -> None:
        qt_date = self.edit_date.date()
        selected_date = date(qt_date.year(), qt_date.month(), qt_date.day())
        trainer_id = self.spin_trainer_id.value()
        training_id = self.spin_training_id.value()

        command = ExecuteScheduleCreation(self._manager, selected_date, trainer_id, training_id)
        if command.execute():
            QMessageBox.information(self, "Success", "Training session added to schedule successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add session to schedule.")
