from PySide6.QtWidgets import QLabel, QLineEdit, QMessageBox, QSpinBox
from src.services.commands import ExecuteTrainingCreation
from src.services.club_manager import ClubManager
from src.gui.dialogs.base_dialog import BaseFormDialog

class CreateTrainingDialog(BaseFormDialog):
    def __init__(self, parent=None):
        self._manager = ClubManager()
        super().__init__(title="Create New Training", width=350, height=280, parent=parent)

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Training Name:"))
        self.edit_name = QLineEdit()
        self.edit_name.setPlaceholderText("Example Name")
        self.main_layout.addWidget(self.edit_name)

        self.main_layout.addWidget(QLabel("Type / Category:"))
        self.edit_type = QLineEdit()
        self.edit_type.setPlaceholderText("Example Type")
        self.main_layout.addWidget(self.edit_type)

        self.main_layout.addWidget(QLabel("Duration (minutes):"))
        self.spin_duration = QSpinBox()
        self.spin_duration.setRange(15, 180)
        self.spin_duration.setValue(60)
        self.main_layout.addWidget(self.spin_duration)

    def _on_confirm_clicked(self) -> None:
        name = self.edit_name.text().strip()
        t_type = self.edit_type.text().strip()
        duration = self.spin_duration.value()

        if not name or not t_type:
            QMessageBox.warning(self, "Error", "All labels must be filled.")
            return

        command = ExecuteTrainingCreation(self._manager, name, t_type, duration)
        if command.execute():
            QMessageBox.information(self, "Success", f"Training type '{name}' created successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to create training.")
