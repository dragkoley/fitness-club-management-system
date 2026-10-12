from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QLabel, QLineEdit, QDateEdit, QMessageBox

from src.services.commands import ExecuteMemberRegistration
from src.services.club_manager import ClubManager
from src.gui.dialogs.base_dialog import BaseFormDialog


class MemberRegistrationDialog(BaseFormDialog):
    def __init__(self, parent=None):
        self._manager = ClubManager()
        super().__init__(
            title="Member Registration",
            width=350,
            height=250,
            parent=parent
        )

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Member Name:"))
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("Example Name")
        self.main_layout.addWidget(self.edit_name)

        self.main_layout.addWidget(QLabel("Birth date:"))
        self.edit_birth_date = QDateEdit()
        self.edit_birth_date.setCalendarPopup(True)
        self.edit_birth_date.setDate(QDate(2000, 1, 1))
        self.main_layout.addWidget(self.edit_birth_date)

        self.main_layout.addWidget(QLabel("Phone number:"))
        self.edit_phone = QLineEdit()
        self.edit_phone.setPlaceholderText("88005553535")
        self.main_layout.addWidget(self.edit_phone)

    def _on_confirm_clicked(self) -> None:
        name = self.edit_name.text().strip()
        phone = self.edit_phone.text().strip()

        qt_birth_date = self.edit_birth_date.date()
        birth_date = date(qt_birth_date.year(), qt_birth_date.month(), qt_birth_date.day())

        if not name or not phone:
            QMessageBox.warning(self, "Error", "All labels must be filled.")
            return

        register_command = ExecuteMemberRegistration(
            manager=self._manager,
            full_name=name,
            birth_date=birth_date,
            phone=phone
        )

        if register_command.execute():
            QMessageBox.information(self, "Success", f"Member {name} registration successful.")
            self.accept()

        else:
            QMessageBox.warning(self, "Error", f"Member registration failed.")