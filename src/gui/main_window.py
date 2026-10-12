from PySide6.QtCore import QSize
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget, QHBoxLayout, QPushButton, QTableWidget, \
    QHeaderView, QTableWidgetItem, QMessageBox

from src.gui.dialogs.member_registration import MemberRegistrationDialog
from src.services.commands import ExecuteSubscriptionSale
from src.database.connection import DatabaseConnection
from src.database.orm_models import MemberORM
from src.services.club_manager import ClubManager
from src.utils.logger import AppLogger


class FitnessClubMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._logger = AppLogger.get_instance()
        self._db = DatabaseConnection.get_instance()
        self._manager = ClubManager()

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.central_widget.setWindowTitle("Fitness Club Manager")
        self.central_widget.setMinimumSize(QSize(1280, 800))

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self._init_reception_tab()
        self._init_schedule_tab()
        self._init_lockers_and_inventory_tab()
        self._init_analytics_tab()

        self._logger.log_info("[GUI] Main window initialized successfully")

    def _init_reception_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)

        button_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_sell_sub = QPushButton("Sell subscription")
        self.btn_register_member = QPushButton("Register Member")

        button_layout.addWidget(self.btn_refresh)
        button_layout.addWidget(self.btn_sell_sub)
        button_layout.addWidget(self.btn_register_member)
        layout.addLayout(button_layout)

        self.member_table = QTableWidget()
        self.member_table.setColumnCount(6)
        self.member_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Birth Date", "Phone", "Subscription type", "Valid until"])
        self.member_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.member_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.member_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.member_table)

        self.btn_refresh.clicked.connect(self.load_members_from_db)
        self.btn_sell_sub.clicked.connect(self.on_sell_subscription_button_click)
        self.btn_register_member.clicked.connect(self.on_register_member_button_click)

        self.tabs.addTab(tab, "Reception and Clients")

        self.load_members_from_db()

    def _init_schedule_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addLayout(layout)
        self.tabs.addTab(tab, "Schedule and Booking")

    def _init_lockers_and_inventory_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addLayout(layout)
        self.tabs.addTab(tab, "Lockers and Inventory")

    def _init_analytics_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addLayout(layout)
        self.tabs.addTab(tab, "Club Analytics")

    def load_members_from_db(self):
        session = self._db.open_session()
        try:
            members = session.query(MemberORM).all()
            self.member_table.setRowCount(len(members))

            for row, member in enumerate(members):
                self.member_table.setItem(row, 0, QTableWidgetItem(str(member.id)))
                self.member_table.setItem(row, 1, QTableWidgetItem(str(member.full_name)))
                self.member_table.setItem(row, 2, QTableWidgetItem(str(member.birth_date)))
                self.member_table.setItem(row, 3, QTableWidgetItem(str(member.phone)))

                if member.subscription:
                    sub_type = str(member.subscription.type)
                    valid_until = member.subscription.end_date.strftime("%d.%m.%Y")
                else:
                    sub_type = "No subscription"
                    valid_until = "-"

                self.member_table.setItem(row, 4, QTableWidgetItem(sub_type))
                self.member_table.setItem(row, 5, QTableWidgetItem(valid_until))

            self._logger.log_info("[GUI] Loaded %d members from database" % len(members))

        except Exception as e:
            self._logger.log_error("[GUI] Failed to load members from database: %s" % e)
            QMessageBox.critical(self, "Error", f"Failed to load members from database: {e}")

        finally:
            self._db.close_session(session, status=True)

    def on_sell_subscription_button_click(self):
        current_row = self.member_table.currentRow()

        if current_row  == -1:
            QMessageBox.warning(self, "Error", "Please, select a member")
            return

        member_id = int(self.member_table.item(current_row, 0).text())

        sale_command = ExecuteSubscriptionSale(
            manager=self._manager,
            member_id=member_id,
            subscription_type="monthly",
            payment_method="card",
            discount_type="student"
        )

        success = sale_command.execute()
        if success:
            self.load_members_from_db()

    def on_register_member_button_click(self):
        dialog = MemberRegistrationDialog(parent=self)
        if dialog.exec():
            self.load_members_from_db()