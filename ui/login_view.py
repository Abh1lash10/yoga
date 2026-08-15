"""
Login Screen for KI.AI — AI-Powered Yoga & Posture Intelligence.
Modern split-screen authentication UI with email/password validation,
show/hide password toggle, and smooth navigation to account creation.
"""

from typing import Any, Dict, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config import settings
from database.database import Database


class LoginView(QWidget):
    """Modern split-screen Login view for KI.AI."""

    login_successful = Signal(dict)       # Emits user_dict
    navigate_to_register = Signal()       # Switch to Register screen

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.password_visible = False
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================
        # LEFT PANEL: KI.AI Branding & Visual Hero
        # ==========================================
        left_panel = QFrame()
        left_panel.setStyleSheet(f"""
            QFrame {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #064E3B, stop:0.5 #0F172A, stop:1 #0B1120);
                border-right: 1px solid {settings.THEME['border_card']};
            }}
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(50, 60, 50, 60)
        left_layout.setSpacing(16)

        left_layout.addStretch()

        # Logo Icon
        logo_icon = QLabel("🧘‍♂️ ✨")
        logo_icon.setStyleSheet("font-size: 46px; background: transparent;")
        logo_icon.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(logo_icon)

        # Brand Title
        brand_title = QLabel("KI.AI")
        brand_title.setStyleSheet(f"font-size: 38px; font-weight: 800; color: {settings.THEME['primary']}; letter-spacing: 2px; background: transparent;")
        brand_title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(brand_title)

        # Subtitle
        brand_subtitle = QLabel("AI-POWERED YOGA & POSTURE INTELLIGENCE")
        brand_subtitle.setStyleSheet("font-size: 11px; font-weight: 700; color: #A7F3D0; letter-spacing: 1.5px; background: transparent;")
        brand_subtitle.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(brand_subtitle)

        # Slogan
        slogan = QLabel("“ Practice smarter. Move better. ”")
        slogan.setStyleSheet("font-size: 15px; font-style: italic; color: #E2E8F0; margin-top: 14px; background: transparent;")
        slogan.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(slogan)

        # Key Features Highlights
        features_card = QFrame()
        features_card.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.60);
                border: 1px solid rgba(16, 185, 129, 0.25);
                border-radius: 12px;
                padding: 16px;
                margin-top: 20px;
            }
        """)
        f_layout = QVBoxLayout(features_card)
        f_layout.setSpacing(10)

        f1 = QLabel("🟢 Real-Time Joint Posture Correction")
        f1.setStyleSheet("color: #F1F5F9; font-size: 12px; font-weight: 500;")
        f_layout.addWidget(f1)

        f2 = QLabel("☀ Guided 12-Step Surya Yoga Sequence")
        f2.setStyleSheet("color: #F1F5F9; font-size: 12px; font-weight: 500;")
        f_layout.addWidget(f2)

        f3 = QLabel("🔒 100% Local & Private Processing")
        f3.setStyleSheet("color: #F1F5F9; font-size: 12px; font-weight: 500;")
        f_layout.addWidget(f3)

        left_layout.addWidget(features_card)
        left_layout.addStretch()

        privacy_note = QLabel("Local AI • No Cloud Video Uploads")
        privacy_note.setStyleSheet("color: #64748B; font-size: 11px; background: transparent;")
        privacy_note.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(privacy_note)

        main_layout.addWidget(left_panel, stretch=5)

        # ==========================================
        # RIGHT PANEL: Login Form Card
        # ==========================================
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {settings.THEME['background']};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(60, 50, 60, 50)
        right_layout.setSpacing(14)

        right_layout.addStretch()

        login_header = QLabel("Sign In to KI.AI")
        login_header.setStyleSheet("font-size: 26px; font-weight: bold; color: #FFFFFF;")
        right_layout.addWidget(login_header)

        login_sub = QLabel("Enter your credentials to access your posture dashboard.")
        login_sub.setStyleSheet(f"color: {settings.THEME['text_secondary']}; font-size: 13px; margin-bottom: 8px;")
        right_layout.addWidget(login_sub)

        # Error / Notification Banner
        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("background-color: rgba(239, 68, 68, 0.15); color: #EF4444; border: 1px solid #EF4444; border-radius: 6px; padding: 8px; font-size: 12px;")
        self.lbl_error.setVisible(False)
        right_layout.addWidget(self.lbl_error)

        # Email Input
        lbl_email = QLabel("Email Address")
        lbl_email.setStyleSheet("font-weight: 600; color: #E2E8F0; font-size: 12px;")
        right_layout.addWidget(lbl_email)

        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("name@example.com")
        self.txt_email.setText("abhilash@ki.ai")  # Pre-filled default demo account
        self.txt_email.setFixedHeight(40)
        right_layout.addWidget(self.txt_email)

        # Password Input
        lbl_pw = QLabel("Password")
        lbl_pw.setStyleSheet("font-weight: 600; color: #E2E8F0; font-size: 12px; margin-top: 4px;")
        right_layout.addWidget(lbl_pw)

        pw_row = QHBoxLayout()
        self.txt_password = QLineEdit()
        self.txt_password.setPlaceholderText("Enter your password")
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setText("password123")  # Pre-filled demo password
        self.txt_password.setFixedHeight(40)
        pw_row.addWidget(self.txt_password)

        self.btn_toggle_pw = QPushButton("👁")
        self.btn_toggle_pw.setFixedSize(40, 40)
        self.btn_toggle_pw.setStyleSheet("""
            QPushButton {
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                border-color: #10B981;
            }
        """)
        self.btn_toggle_pw.clicked.connect(self._toggle_password_visibility)
        pw_row.addWidget(self.btn_toggle_pw)
        right_layout.addLayout(pw_row)

        # Forgot Password Link
        forgot_row = QHBoxLayout()
        forgot_row.addStretch()
        btn_forgot = QPushButton("Forgot Password?")
        btn_forgot.setStyleSheet("color: #10B981; font-size: 11px; background: transparent; border: none; font-weight: 500;")
        btn_forgot.clicked.connect(self._on_forgot_password)
        forgot_row.addWidget(btn_forgot)
        right_layout.addLayout(forgot_row)

        # Login Action Button
        self.btn_login = QPushButton("LOGIN")
        self.btn_login.setProperty("class", "btn_primary")
        self.btn_login.setFixedHeight(42)
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {settings.THEME['primary']};
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {settings.THEME['primary_hover']};
            }}
        """)
        self.btn_login.clicked.connect(self._on_login_clicked)
        right_layout.addWidget(self.btn_login)

        # Divider
        div_row = QHBoxLayout()
        div_left = QFrame()
        div_left.setFrameShape(QFrame.HLine)
        div_left.setStyleSheet("color: #334155;")
        div_right = QFrame()
        div_right.setFrameShape(QFrame.HLine)
        div_right.setStyleSheet("color: #334155;")
        div_text = QLabel("OR")
        div_text.setStyleSheet("color: #64748B; font-size: 11px; padding: 0 8px;")
        div_row.addWidget(div_left)
        div_row.addWidget(div_text)
        div_row.addWidget(div_right)
        right_layout.addLayout(div_row)

        # Create Account Button
        self.btn_register = QPushButton("CREATE ACCOUNT")
        self.btn_register.setProperty("class", "btn_secondary")
        self.btn_register.setFixedHeight(40)
        self.btn_register.clicked.connect(self.navigate_to_register.emit)
        right_layout.addWidget(self.btn_register)

        right_layout.addStretch()

        # Enter key triggers login
        self.txt_password.returnPressed.connect(self._on_login_clicked)
        self.txt_email.returnPressed.connect(self._on_login_clicked)

        main_layout.addWidget(right_panel, stretch=6)

    def _toggle_password_visibility(self) -> None:
        self.password_visible = not self.password_visible
        if self.password_visible:
            self.txt_password.setEchoMode(QLineEdit.Normal)
            self.btn_toggle_pw.setText("🔒")
        else:
            self.txt_password.setEchoMode(QLineEdit.Password)
            self.btn_toggle_pw.setText("👁")

    def _on_login_clicked(self) -> None:
        email = self.txt_email.text().strip()
        password = self.txt_password.text()

        if not email or not password:
            self._show_error("Please enter both email and password.")
            return

        success, message, user = self.db.authenticate_user(email, password)
        if success and user:
            self.lbl_error.setVisible(False)
            self.login_successful.emit(user)
        else:
            self._show_error(message or "Invalid email or password.")

    def _show_error(self, msg: str) -> None:
        self.lbl_error.setText(f"⚠️ {msg}")
        self.lbl_error.setVisible(True)

    def _on_forgot_password(self) -> None:
        QMessageBox.information(
            self,
            "Password Reset",
            "To reset your password in local offline mode, please register a new profile or use default credentials:\n\nEmail: abhilash@ki.ai\nPassword: password123",
        )
