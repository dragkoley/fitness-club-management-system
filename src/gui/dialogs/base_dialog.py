from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton


class BaseFormDialog(QDialog):
    def __init__(self, title: str, width: int = 350, height: int = 250, parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.setFixedSize(width, height)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.main_layout = QVBoxLayout(self)
        self._initialize_dialog_structure()

    def _initialize_dialog_structure(self) -> None:
        self._setup_fields()
        self.main_layout.addSpacing(15)
        self._setup_buttons()

    def _setup_fields(self) -> None:
        raise NotImplementedError()

    def _setup_buttons(self) -> None:
        buttons_layout = QHBoxLayout()
        self.btn_cancel = QPushButton("Cancel")
        self.btn_confirm = QPushButton("Confirm")

        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_confirm)
        self.main_layout.addLayout(buttons_layout)

        self.btn_cancel.clicked.connect(self.reject)
        self.btn_confirm.clicked.connect(self._on_confirm_clicked)

    def _on_confirm_clicked(self) -> None:
        raise NotImplementedError()
