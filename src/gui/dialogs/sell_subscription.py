from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QMessageBox

from src.services.club_manager import ClubManager
from src.services.commands import ExecuteSubscriptionSale
from src.gui.dialogs.base_dialog import BaseFormDialog


class SellSubscriptionDialog(BaseFormDialog):
    def __init__(self, member_id: int, member_name: str, parent=None):
        self._manager = ClubManager()
        self._member_id = member_id
        title = f"Subscription for {member_name} (ID: {member_id})"
        super().__init__(
            title=title,
            width=380,
            height=280,
            parent=parent
        )

    def _setup_fields(self) -> None:
        self.main_layout.addWidget(QtWidgets.QLabel("Select Subscription Type"))
        self.combo_sub_type = QtWidgets.QComboBox()
        self.combo_sub_type.addItem("Monthly Plan (30 days)", "monthly")
        self.combo_sub_type.addItem("Yearly Plan (365 days)", "year")
        self.main_layout.addWidget(self.combo_sub_type)

        self.main_layout.addWidget(QtWidgets.QLabel("Select Discount Type"))
        self.combo_discount_type = QtWidgets.QComboBox()
        self.combo_discount_type.addItem("No Discount (Standard)", "none")
        self.combo_discount_type.addItem("Student Discount (20%)", "student")
        self.combo_discount_type.addItem("Corporate Discount (15%)", "corporate")
        self.main_layout.addWidget(self.combo_discount_type)

        self.main_layout.addWidget(QtWidgets.QLabel("Select Payment Method"))
        self.combo_payment_method = QtWidgets.QComboBox()
        self.combo_payment_method.addItem("Bank Card", "card")
        self.combo_payment_method.addItem("Cash", "cash")
        self.main_layout.addWidget(self.combo_payment_method)

        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(QtWidgets.QLabel("Final Price:"))
        self.price_value = QtWidgets.QLabel("Select Plan")
        self.price_value.setStyleSheet("color: green")
        self.main_layout.addWidget(self.price_value)

        self.combo_sub_type.currentIndexChanged.connect(self._update_price_value)
        self.combo_discount_type.currentIndexChanged.connect(self._update_price_value)

    def _update_price_value(self) -> None:
        sub_type = self.combo_sub_type.currentData()
        discount_type = self.combo_discount_type.currentData()
        calculated_price = self._manager.calculate_preview_price(sub_type, discount_type)
        self.price_value.setText(f"{calculated_price} rub")

    def _on_confirm_clicked(self) -> None:
        sub_type = self.combo_sub_type.currentData()
        discount_type = self.combo_discount_type.currentData()
        payment_method = self.combo_payment_method.currentData()

        sale_command = ExecuteSubscriptionSale(
            manager=self._manager,
            member_id=self._member_id,
            subscription_type=sub_type,
            payment_method=payment_method,
            discount_type=discount_type,
        )

        if sale_command.execute():
            QtWidgets.QMessageBox.information(self, "Success", "Subscription was successfully issued.")
            self.accept()

        else:
            QMessageBox.critical(self, "Error", "Failed to issue subscription.")

