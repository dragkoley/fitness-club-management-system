from PySide6.QtWidgets import QLabel, QLineEdit, QMessageBox

from src.gui.dialogs.base_dialog import BaseFormDialog
from src.services.club_manager import ClubManager
from src.services.commands import ExecuteTrainerRegistration, ExecuteTrainerUpdate


class TrainerFormDialog(BaseFormDialog):
    def __init__(self,
                 trainer_id: int | None = None,
                 current_name: str = "",
                 current_phone: str = "",
                 current_speciality: str = "",
                 current_experience: str = "",
                 parent=None):

        self._manager = ClubManager()
        self._trainer_id = trainer_id

        self._is_edit_mode = trainer_id is not None

        self._initial_name = current_name
        self._initial_phone = current_phone
        self._initial_speciality = current_speciality
        self._initial_experience = current_experience

        title = f"Edit Trainer Profile — ID {trainer_id}" if self._is_edit_mode else "Trainer Registration"

        super().__init__(title=title, width=350, height=280, parent=parent)

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Trainer Name:"))
        self.edit_name = QLineEdit()
        self.edit_name.setText(self._initial_name)
        if not self._is_edit_mode:
            self.edit_name.setPlaceholderText("Example Name")
        self.main_layout.addWidget(self.edit_name)

        self.main_layout.addWidget(QLabel("Speciality:"))
        self.edit_speciality = QLineEdit()
        self.edit_speciality.setText(self._initial_speciality)
        if not self._is_edit_mode:
            self.edit_speciality.setPlaceholderText("Example Speciality")
        self.main_layout.addWidget(self.edit_speciality)

        self.main_layout.addWidget(QLabel("Phone number:"))
        self.edit_phone = QLineEdit()
        self.edit_phone.setText(self._initial_phone)
        if not self._is_edit_mode:
            self.edit_phone.setPlaceholderText("88005553535")
        self.main_layout.addWidget(self.edit_phone)

        self.main_layout.addWidget(QLabel("Experience:"))
        self.edit_experience = QLineEdit()
        self.edit_experience.setText(self._initial_experience)
        if not self._is_edit_mode:
            self.edit_experience.setPlaceholderText("Example Experience")
        self.main_layout.addWidget(self.edit_experience)

    def _on_confirm_clicked(self) -> None:
        name = self.edit_name.text().strip()
        phone = self.edit_phone.text().strip()
        experience = self.edit_experience.text().strip()
        speciality = self.edit_speciality.text().strip()

        if not name or not phone or not experience or not speciality:
            QMessageBox.warning(self, "Error", "All fields must be filled.")
            return

        if self._is_edit_mode:
            command = ExecuteTrainerUpdate(
                manager=self._manager,
                trainer_id=self._trainer_id,
                full_name=name,
                phone=phone,
                speciality=speciality,
                experience=experience
            )
            success_msg = f"Trainer '{name}' profile updated successfully."
            error_msg = "Failed to update trainer profile."
        else:
            command = ExecuteTrainerRegistration(
                manager=self._manager,
                full_name=name,
                phone=phone,
                speciality=speciality,
                experience=experience
            )
            success_msg = f"Trainer {name} registration successful."
            error_msg = "Trainer registration failed."

        if command.execute():
            QMessageBox.information(self, "Success", success_msg)
            self.accept()
        else:
            QMessageBox.warning(self, "Error", error_msg)
