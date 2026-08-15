"""
Registration Screen for KI.AI.
Provides user signup with goals, difficulty selection, field validation,
and instant redirection to Login.
"""

from typing import Any, Dict, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from config import settings
from database.database import Database


class RegisterView(QWidget):
    """User Registration Screen for KI.AI."""

    registration_successful = Signal()
    navigate_to_login = Signal()

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Left Panel (Branding)
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #064E3B, stop:0.5 #0F172A, stop:1 #0B1120);
                border-right: 1px solid {settings.THEME['border_card']};
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 60, 50, 60)
        left_layout.setSpacing(14)
        left_layout.addStretch()

        logo_icon = QLabel("🧘 ✨")
        logo_icon.setStyleSheet("font-size: 40px; background: transparent;")
        logo_icon.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_icon)

        brand_title = QLabel("KI.AI")
        brand_title.setStyleSheet(f"font-size: 34px; font-weight: 800; color: {settings.THEME['primary']}; letter-spacing: 2px; background: transparent;")
        brand_title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(brand_title)

        slogan = QLabel("Create Your Posture Profile")
        slogan.setStyleSheet("font-size: 16px; font-weight: 600; color: #FFFFFF; background: transparent;")
        slogan.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(slogan)

        subtext = QLabel("Personalize AI recommendations, track accuracy over time, and master both classic yoga poses & Surya Namaskar.")
        subtext.setStyleSheet("color: #94A3B8; font-size: 12px; line-height: 1.5; margin-top: 8px; background: transparent;")
        subtext.setWordWrap(True)
        subtext.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(subtext)

        left_layout.addStretch()
        main_layout.addWidget(left_panel, stretch=4)

        # Right Panel (Form Card)
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {settings.THEME['background']};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 40, 60, 40)
        right_layout.setSpacing(10)
        right_layout.addStretch()

        title = QLabel("Create Account")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #FFFFFF;")
        right_layout.addWidget(title)

        subtitle = QLabel("Join KI.AI and begin your posture training journey.")
        subtitle.setStyleSheet("color: #94A3B8; font-size: 12px; margin-bottom: 6px;")
        right_layout.addWidget(subtitle)

        # Error / Success Banner
        self.lbl_msg = QLabel("")
        self.lbl_msg.setVisible(False)
        right_layout.addWidget(self.lbl_msg)

        grid = QGridLayout()
        grid.setSpacing(10)

        # Full Name
        grid.addWidget(QLabel("Full Name *"), 0, 0)
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("e.g. Abhilash Sharma")
        self.txt_name.setFixedHeight(36)
        grid.addWidget(self.txt_name, 1, 0)

        # Age
        grid.addWidget(QLabel("Age"), 0, 1)
        self.spin_age = QSpinBox()
        self.spin_age.setRange(10, 100)
        self.spin_age.setValue(23)
        self.spin_age.setFixedHeight(36)
        self.spin_age.setStyleSheet("background-color: #0F172A; border: 1px solid #334155; border-radius: 6px; padding: 4px 8px; color: white;")
        grid.addWidget(self.spin_age, 1, 1)

        # Experience Level
        grid.addWidget(QLabel("Experience Level"), 2, 0)
        self.combo_exp = QComboBox()
        self.combo_exp.addItems(settings.DIFFICULTY_LEVELS)
        self.combo_exp.setFixedHeight(36)
        grid.addWidget(self.combo_exp, 3, 0)

        # Primary Goal
        grid.addWidget(QLabel("Primary Goal"), 2, 1)
        self.combo_goal = QComboBox()
        self.combo_goal.addItems(settings.GOALS)
        self.combo_goal.setFixedHeight(36)
        grid.addWidget(self.combo_goal, 3, 1)

        # Email
        grid.addWidget(QLabel("Email Address *"), 4, 0, 1, 2)
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("name@example.com")
        self.txt_email.setFixedHeight(36)
        grid.addWidget(self.txt_email, 5, 0, 1, 2)

        # Password
        grid.addWidget(QLabel("Password *"), 6, 0)
        self.txt_pw = QLineEdit()
        self.txt_pw.setEchoMode(QLineEdit.Password)
        self.txt_pw.setPlaceholderText("At least 6 characters")
        self.txt_pw.setFixedHeight(36)
        grid.addWidget(self.txt_pw, 7, 0)

        # Confirm Password
        grid.addWidget(QLabel("Confirm Password *"), 6, 1)
        self.txt_confirm_pw = QLineEdit()
        self.txt_confirm_pw.setEchoMode(QLineEdit.Password)
        self.txt_confirm_pw.setPlaceholderText("Re-type password")
        self.txt_confirm_pw.setFixedHeight(36)
        grid.addWidget(self.txt_confirm_pw, 7, 1)

        right_layout.addLayout(grid)

        # Submit Buttons
        right_layout.addSpacing(6)
        self.btn_submit = QPushButton("CREATE ACCOUNT")
        self.btn_submit.setFixedHeight(40)
        self.btn_submit.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.THEME['primary']};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {settings.THEME['primary_hover']};
            }}
        """)
        self.btn_submit.clicked.connect(self._on_register_clicked)
        right_layout.addWidget(self.btn_submit)

        self.btn_back_login = QPushButton("BACK TO LOGIN")
        self.btn_back_login.setProperty("class", "btn_secondary")
        self.btn_back_login.setFixedHeight(38)
        self.btn_back_login.clicked.connect(self.navigate_to_login.emit)
        right_layout.addWidget(self.btn_back_login)

        right_layout.addStretch()
        main_layout.addWidget(right_panel, stretch=6)

    def _on_register_clicked(self) -> None:
        name = self.txt_name.text().strip()
        email = self.txt_email.text().strip()
        age = self.spin_age.value()
        exp = self.combo_exp.currentText()
        goal = self.combo_goal.currentText()
        pw = self.txt_pw.text()
        confirm_pw = self.txt_confirm_pw.text()

        if not name:
            self._show_msg("Please enter your full name.", is_error=True)
            return
        if not email or "@" not in email:
            self._show_msg("Please enter a valid email address.", is_error=True)
            return
        if len(pw) < 6:
            self._show_msg("Password must be at least 6 characters.", is_error=True)
            return
        if pw != confirm_pw:
            self._show_msg("Passwords do not match.", is_error=True)
            return

        success, msg, user = self.db.register_user(
            name=name,
            email=email,
            password=pw,
            age=age,
            experience=exp,
            goal=goal,
        )

        if success:
            QMessageBox.information(self, "Success", "Account created successfully! You can now log in.")
            self.navigate_to_login.emit()
        else:
            self._show_msg(msg, is_error=True)

    def _show_msg(self, text: str, is_error: bool = True) -> None:
        color = "#EF4444" if is_error else "#10B981"
        bg = "rgba(239, 68, 68, 0.15)" if is_error else "rgba(16, 185, 129, 0.15)"
        self.lbl_msg.setText(f"⚠️ {text}" if is_error else f"✓ {text}")
        self.lbl_msg.setStyleSheet(f"background-color: {bg}; color: {color}; border: 1px solid {color}; border-radius: 6px; padding: 8px; font-size: 12px;")
        self.lbl_msg.setVisible(True)
