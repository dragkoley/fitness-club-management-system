from PySide6.QtWidgets import QLabel, QLineEdit, QMessageBox

from src.gui.dialogs.base_dialog import BaseFormDialog
from src.services.club_manager import ClubManager
from src.services.commands import ExecuteTrainerRegistration


class TrainerRegistrationDialog(BaseFormDialog):
    def __init__(self, parent=None):
        self._manager = ClubManager()
        super().__init__(
            title="Trainer Registration",
            width=350,
            height=250,
            parent=parent
        )

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Trainer Name:"))
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("Example Name")
        self.main_layout.addWidget(self.edit_name)

        self.main_layout.addWidget(QLabel("Speciality:"))
        self.edit_speciality = QLineEdit()
        self.edit_speciality.setPlaceholderText("Example Speciality")
        self.main_layout.addWidget(self.edit_speciality)

        self.main_layout.addWidget(QLabel("Phone number:"))
        self.edit_phone = QLineEdit()
        self.edit_phone.setPlaceholderText("88005553535")
        self.main_layout.addWidget(self.edit_phone)

        self.main_layout.addWidget(QLabel("Experience:"))
        self.edit_experience = QLineEdit()
        self.edit_experience.setPlaceholderText("Example Experience")
        self.main_layout.addWidget(self.edit_experience)

    def _on_confirm_clicked(self) -> None:
        name = self.edit_name.text().strip()
        phone = self.edit_phone.text().strip()
        experience = self.edit_experience.text().strip()
        speciality = self.edit_speciality.text().strip()

        if not name or not phone or not experience or not speciality:
            QMessageBox.warning(self, "Error", "All labels must be filled.")
            return

        register_command = ExecuteTrainerRegistration(
            manager=self._manager,
            full_name=name,
            phone=phone,
            speciality=speciality,
            experience=experience,
        )

        if register_command.execute():
            QMessageBox.information(self, "Success", f"Member {name} registration successful.")
            self.accept()

        else:
            QMessageBox.warning(self, "Error", f"Member registration failed.")
