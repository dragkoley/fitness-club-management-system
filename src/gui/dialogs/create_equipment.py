from datetime import date
from PySide6.QtCore import QDate
from PySide6.QtWidgets import QLabel, QLineEdit, QDateEdit, QComboBox, QMessageBox
from src.gui.dialogs.base_dialog import BaseFormDialog
from src.services.commands import ExecuteEquipmentAdding
from src.services.club_manager import ClubManager


class CreateEquipmentDialog(BaseFormDialog):
    def __init__(self, parent=None):
        self._manager = ClubManager()
        super().__init__(title="Add New Equipment", width=360, height=280, parent=parent)

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Equipment / Machine Name:"))
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("e.g. Treadmill Matrix T5x")
        self.main_layout.addWidget(self.edit_name)

        self.main_layout.addWidget(QLabel("Initial Technical State:"))
        self.combo_state = QComboBox()
        self.combo_state.addItems(["Excellent", "Good", "Needs Service", "In Repair"])
        self.main_layout.addWidget(self.combo_state)

        self.main_layout.addWidget(QLabel("Date of Purchase:"))
        self.edit_date = QDateEdit()
        self.edit_date.setCalendarPopup(True)
        self.edit_date.setDate(QDate.currentDate())
        self.main_layout.addWidget(self.edit_date)

    def _on_confirm_clicked(self) -> None:
        name = self.edit_name.text().strip()
        state = self.combo_state.currentText()

        qt_date = self.edit_date.date()
        purchase_date = date(qt_date.year(), qt_date.month(), qt_date.day())

        if not name:
            QMessageBox.warning(self, "Error", "Equipment name cannot be empty.")
            return

        command = ExecuteEquipmentAdding(
            manager=self._manager,
            name=name,
            state=state,
            date_purchase=purchase_date
        )

        if command.execute():
            QMessageBox.information(self, "Success", f"Equipment '{name}' added successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to register new equipment in the database.")
