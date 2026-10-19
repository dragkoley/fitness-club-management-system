from PySide6.QtWidgets import QLabel, QComboBox, QMessageBox
from src.gui.dialogs.base_dialog import BaseFormDialog
from src.services.commands import ExecuteEquipmentStateUpdate
from src.services.club_manager import ClubManager


class ChangeEquipmentStateDialog(BaseFormDialog):
    def __init__(self, equipment_id: int, current_name: str, current_state: str, parent=None):
        self._manager = ClubManager()
        self._equipment_id = equipment_id
        self._current_state = current_state

        title = f"Service Status — ID {equipment_id}"
        super().__init__(title=title, width=350, height=180, parent=parent)

        index = self.combo_state.findText(self._current_state)
        if index >= 0:
            self.combo_state.setCurrentIndex(index)

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QLabel("Select New Maintenance/Service State:"))
        self.combo_state = QComboBox()
        self.combo_state.addItems(["Excellent", "Good", "Needs Service", "In Repair", "Broken / To Decommission"])
        self.main_layout.addWidget(self.combo_state)

    def _on_confirm_clicked(self) -> None:
        new_state = self.combo_state.currentText()

        command = ExecuteEquipmentStateUpdate(
            manager=self._manager,
            equipment_id=self._equipment_id,
            new_state=new_state
        )

        if command.execute():
            QMessageBox.information(self, "Success", "Equipment technical status updated.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update status on database layer.")
