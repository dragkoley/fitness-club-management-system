from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import QLabel, QLineEdit, QDateEdit, QMessageBox

from src.services.commands import ExecuteMemberUpdate
from src.services.commands import ExecuteMemberRegistration
from src.services.club_manager import ClubManager
from src.gui.dialogs.base_dialog import BaseFormDialog


class MemberFormDialog(BaseFormDialog):
    def __init__(
            self,
            member_id: int | None = None,
            current_name: str = "",
            current_birth_date: date | None = None,
            current_phone: str = "" ,
            parent=None
    ):
        self._manager = ClubManager()

        self._member_id = member_id
        self._is_edit_mode = member_id is not None
        self._initial_name = current_name
        self._initial_birth_date = current_birth_date
        self._initial_phone = current_phone

        title = "Edit Member" if self._is_edit_mode else "Member Registration"

        super().__init__(
            title=title,
            width=350,
            height=250,
            parent=parent
        )

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Full Name:"))
        self.edit_name = QLineEdit()
        self.edit_name.setText(self._initial_name)
        if not self._is_edit_mode:
            self.edit_name.setPlaceholderText("Ivan Ivanov")
        self.main_layout.addWidget(self.edit_name)

        self.main_layout.addWidget(QLabel("Birth date:"))
        self.edit_birth_date = QDateEdit()
        self.edit_birth_date.setCalendarPopup(True)
        if self._is_edit_mode:
            self.edit_birth_date.setDate(QDate(
                self._initial_birth_date.year,
                self._initial_birth_date.month,
                self._initial_birth_date.day)
            )
        else:
            self.edit_birth_date.setDate(QDate(2000, 1, 1))
        self.main_layout.addWidget(self.edit_birth_date)

        self.main_layout.addWidget(QLabel("Phone number:"))
        self.edit_phone = QLineEdit()
        self.edit_phone.setText(self._initial_phone)
        if not self._is_edit_mode:
            self.edit_phone.setPlaceholderText("12345678912")
        self.main_layout.addWidget(self.edit_phone)

    def _on_confirm_clicked(self) -> None:
        name = self.edit_name.text().strip()
        phone = self.edit_phone.text().strip()

        qt_birth_date = self.edit_birth_date.date()
        birth_date = date(qt_birth_date.year(), qt_birth_date.month(), qt_birth_date.day())

        if not name or not phone:
            QMessageBox.warning(self, "Error", "All labels must be filled.")
            return

        if self._is_edit_mode:
            command = ExecuteMemberUpdate(
                manager=self._manager,
                member_id=self._member_id,
                full_name=name,
                birth_date=birth_date,
                phone=phone
            )


        else:
            command = ExecuteMemberRegistration(
                manager=self._manager,
                full_name=name,
                birth_date=birth_date,
                phone=phone
            )

        if command.execute():
            QMessageBox.information(self, "Success", f"Member {name} updating successful.")
            self.accept()

        else:
            QMessageBox.warning(self, "Error", f"Member updating failed.")