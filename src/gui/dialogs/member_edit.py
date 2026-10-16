from PySide6.QtWidgets import QLabel, QLineEdit, QMessageBox
from src.gui.dialogs.base_dialog import BaseFormDialog
from src.services.commands import ExecuteMemberUpdate
from src.services.club_manager import ClubManager


class MemberEditDialog(BaseFormDialog):
    def __init__(self, member_id: int, current_name: str, current_phone: str, parent=None):
        self._manager = ClubManager()
        self._member_id = member_id
        self._initial_name = current_name
        self._initial_phone = current_phone

        super().__init__(title=f"Edit Profile — ID {member_id}", width=350, height=240, parent=parent)

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Full Name:"))
        self.edit_name = QLineEdit()
        self.edit_name.setText(self._initial_name)
        self.main_layout.addWidget(self.edit_name)

        self.main_layout.addWidget(QLabel("Phone Number:"))
        self.edit_phone = QLineEdit()
        self.edit_phone.setText(self._initial_phone)
        self.main_layout.addWidget(self.edit_phone)

    def _on_confirm_clicked(self) -> None:
        name = self.edit_name.text().strip()
        phone = self.edit_phone.text().strip()

        if not name or not phone:
            QMessageBox.warning(self, "Error", "All fields must be filled.")
            return

        update_command = ExecuteMemberUpdate(
            manager=self._manager,
            member_id=self._member_id,
            full_name=name,
            phone=phone
        )

        if update_command.execute():
            QMessageBox.information(self, "Success", "Profile updated successfully.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update profile. This phone number might be already in use.")
