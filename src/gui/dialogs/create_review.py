from PySide6.QtWidgets import QLabel, QSpinBox, QLineEdit, QMessageBox

from src.gui.dialogs.base_dialog import BaseFormDialog
from src.services.club_manager import ClubManager
from src.services.commands import ExecuteReviewCreation


class CreateReviewDialog(BaseFormDialog):
    def __init__(self, parent=None):
        self.manager = ClubManager()
        super().__init__(title="Create Review", width=360, height=260, parent=parent)

    def _setup_fields(self):
        self.main_layout.addWidget(QLabel("Member ID:"))
        self.spin_member_id = QSpinBox()
        self.spin_member_id.setMinimum(1)
        self.main_layout.addWidget(self.spin_member_id)

        self.main_layout.addWidget(QLabel("Rating / Mark (1 to 5):"))
        self.spin_mark = QSpinBox()
        self.spin_mark.setRange(1, 5)
        self.spin_mark.setValue(5)
        self.main_layout.addWidget(self.spin_mark)

        self.main_layout.addWidget(QLabel("Comment:"))
        self.edit_text = QLineEdit()
        self.edit_text.setPlaceholderText("Enter your comment here...")
        self.main_layout.addWidget(self.edit_text)

    def _on_confirm_clicked(self):
        member_id = self.spin_member_id.value()
        mark = self.spin_mark.value()
        text = self.edit_text.text()

        if not text:
            QMessageBox.warning(self, "Error", "Please enter a comment.")
            return

        command = ExecuteReviewCreation(
            manager=self.manager,
            member_id=member_id,
            mark=mark,
            text=text,
        )

        if command.execute():
            QMessageBox.information(self, "Success", "Review created successfully.")
            self.accept()

        else:
            QMessageBox.warning(self, "Error", "Failed to create review.")
