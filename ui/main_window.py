"""
Main Application Window for KI.AI.
Hosts the left sidebar navigation, top header greeting, and stacked views across:
Dashboard, Yoga Library, Surya Yoga, Live Practice, Recommendations, History,
Progress Analytics, Custom Poses, Profile, Settings, and Logout.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from config import settings
from database.database import Database
from ui.add_pose_window import AddPoseWindow
from ui.camera_window import CameraWindow
from ui.history_window import HistoryWindow
from ui.home_window import HomeWindow
from ui.profile_window import ProfileWindow
from ui.progress_window import ProgressWindow
from ui.recommendation_window import RecommendationWindow
from ui.settings_window import SettingsWindow
from ui.surya_yoga_window import SuryaYogaWindow
from ui.yoga_library import YogaLibrary

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main window for KI.AI desktop application."""

    logout_requested = Signal()

    def __init__(self, db: Database, user: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.db = db
        self.user = user or self.db.get_user_by_id(1) or {"id": 1, "name": "Abhilash", "goal": "General Fitness"}

        self.setWindowTitle(settings.WINDOW_TITLE)
        self.setMinimumSize(1300, 840)
        self._init_ui()
        self._connect_signals()

    def _get_time_greeting(self) -> str:
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning"
        elif hour < 18:
            return "Good afternoon"
        return "Good evening"

    def _init_ui(self) -> None:
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ==========================================
        # 1. Left Sidebar Navigation
        # ==========================================
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        side_layout = QVBoxLayout(sidebar)
        side_layout.setContentsMargins(14, 18, 14, 18)
        side_layout.setSpacing(4)

        # Brand Header
        brand_box = QHBoxLayout()
        logo_icon = QLabel("🧘")
        logo_icon.setStyleSheet("font-size: 26px; background: transparent;")
        brand_box.addWidget(logo_icon)

        title_col = QVBoxLayout()
        app_title = QLabel("KI.AI")
        app_title.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {settings.THEME['primary']}; letter-spacing: 1.5px;")
        app_sub = QLabel("Posture Intelligence")
        app_sub.setStyleSheet("color: #64748B; font-size: 10px; font-weight: 600; letter-spacing: 0.5px;")
        title_col.addWidget(app_title)
        title_col.addWidget(app_sub)
        brand_box.addLayout(title_col)
        side_layout.addLayout(brand_box)
        side_layout.addSpacing(14)

        # Nav Buttons Group
        self.nav_btn_group = QButtonGroup(self)
        self.nav_btn_group.setExclusive(True)

        self.btn_nav_dash = self._create_nav_button("🏠  Dashboard", 0)
        self.btn_nav_library = self._create_nav_button("🧘  Yoga Library", 1)
        self.btn_nav_surya = self._create_nav_button("☀  Surya Yoga", 2)
        self.btn_nav_practice = self._create_nav_button("🎥  Live Practice", 3)
        self.btn_nav_recom = self._create_nav_button("✨  Recommendations", 4)
        self.btn_nav_history = self._create_nav_button("🕘  History", 5)
        self.btn_nav_progress = self._create_nav_button("📈  Progress", 6)
        self.btn_nav_custom = self._create_nav_button("➕  Custom Poses", 7)
        self.btn_nav_profile = self._create_nav_button("👤  Profile", 8)
        self.btn_nav_settings = self._create_nav_button("⚙  Settings", 9)

        side_layout.addWidget(self.btn_nav_dash)
        side_layout.addWidget(self.btn_nav_library)
        side_layout.addWidget(self.btn_nav_surya)
        side_layout.addWidget(self.btn_nav_practice)
        side_layout.addWidget(self.btn_nav_recom)
        side_layout.addWidget(self.btn_nav_history)
        side_layout.addWidget(self.btn_nav_progress)
        side_layout.addWidget(self.btn_nav_custom)
        side_layout.addWidget(self.btn_nav_profile)
        side_layout.addWidget(self.btn_nav_settings)

        side_layout.addStretch()

        # Logout Button
        btn_logout = QPushButton("🚪  Logout")
        btn_logout.setProperty("class", "nav_btn")
        btn_logout.clicked.connect(self._on_logout)
        side_layout.addWidget(btn_logout)

        main_layout.addWidget(sidebar)

        # ==========================================
        # 2. Right Main Layout (Header + Stack Views)
        # ==========================================
        content_container = QWidget()
        right_layout = QVBoxLayout(content_container)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Top Header Bar
        top_header = QFrame()
        top_header.setObjectName("top_header")
        top_header.setFixedHeight(60)
        th_layout = QHBoxLayout(top_header)
        th_layout.setContentsMargins(24, 0, 24, 0)

        self.lbl_page_title = QLabel("Dashboard")
        self.lbl_page_title.setStyleSheet("font-size: 17px; font-weight: 700; color: #FFFFFF;")
        th_layout.addWidget(self.lbl_page_title)
        th_layout.addStretch()

        # Privacy Badge
        privacy_badge = QLabel("🔒 100% Local AI")
        privacy_badge.setStyleSheet("background-color: rgba(16, 185, 129, 0.12); color: #10B981; border: 1px solid #10B981; border-radius: 12px; padding: 3px 10px; font-size: 11px; font-weight: 600; margin-right: 12px;")
        th_layout.addWidget(privacy_badge)

        # Greeting & User Avatar
        user_name = self.user.get("name", "Abhilash")
        self.lbl_greeting = QLabel(f"{self._get_time_greeting()}, {user_name}")
        self.lbl_greeting.setStyleSheet("color: #E2E8F0; font-weight: 600; font-size: 13px;")
        th_layout.addWidget(self.lbl_greeting)

        avatar_lbl = QLabel(user_name[0].upper() if user_name else "U")
        avatar_lbl.setFixedSize(32, 32)
        avatar_lbl.setAlignment(Qt.AlignCenter)
        avatar_lbl.setStyleSheet("background-color: #064E3B; color: #10B981; border: 1px solid #10B981; border-radius: 16px; font-weight: bold; margin-left: 8px;")
        th_layout.addWidget(avatar_lbl)

        right_layout.addWidget(top_header)

        # Stacked Views Container
        self.stacked_widget = QStackedWidget()

        # Instantiate View Pages
        self.page_home = HomeWindow(self.db, self.user)
        self.page_library = YogaLibrary(self.db)
        self.page_surya = SuryaYogaWindow(self.db, self.user)
        self.page_camera = CameraWindow(self.db, self.user)
        self.page_recommendations = RecommendationWindow(self.db, self.user)
        self.page_history = HistoryWindow(self.db, self.user)
        self.page_progress = ProgressWindow(self.db, self.user)
        self.page_add_pose = AddPoseWindow(self.db, self.user)
        self.page_profile = ProfileWindow(self.db, self.user)
        self.page_settings = SettingsWindow(self.db)

        self.stacked_widget.addWidget(self.page_home)             # Index 0
        self.stacked_widget.addWidget(self.page_library)          # Index 1
        self.stacked_widget.addWidget(self.page_surya)            # Index 2
        self.stacked_widget.addWidget(self.page_camera)           # Index 3
        self.stacked_widget.addWidget(self.page_recommendations)  # Index 4
        self.stacked_widget.addWidget(self.page_history)          # Index 5
        self.stacked_widget.addWidget(self.page_progress)         # Index 6
        self.stacked_widget.addWidget(self.page_add_pose)         # Index 7
        self.stacked_widget.addWidget(self.page_profile)          # Index 8
        self.stacked_widget.addWidget(self.page_settings)         # Index 9

        right_layout.addWidget(self.stacked_widget)
        main_layout.addWidget(content_container)

        self.btn_nav_dash.setChecked(True)

    def _create_nav_button(self, text: str, index: int) -> QPushButton:
        btn = QPushButton(text)
        btn.setProperty("class", "nav_btn")
        btn.setCheckable(True)
        btn.clicked.connect(lambda: self.switch_page(index))
        self.nav_btn_group.addButton(btn, index)
        return btn

    def switch_page(self, index: int) -> None:
        titles = [
            "Dashboard", "Yoga Library", "Surya Yoga (12 Steps)", "Live Practice",
            "Recommendations", "Practice History", "Progress & Analytics",
            "Custom Pose Creator", "Profile", "System Settings"
        ]
        self.lbl_page_title.setText(titles[index] if index < len(titles) else "KI.AI")
        self.stacked_widget.setCurrentIndex(index)

        # Camera lifecycle management
        if index == 3:
            self.page_camera.start_camera()
        else:
            self.page_camera.stop_camera()

        if index == 2:
            self.page_surya.start_camera()
        else:
            self.page_surya.stop_camera()

        if index == 0:
            self.page_home.refresh_dashboard()
        elif index == 5:
            self.page_history.refresh_history()
        elif index == 6:
            self.page_progress.refresh_charts()

    def _connect_signals(self) -> None:
        self.page_home.start_practice_clicked.connect(self._on_start_practice_pose)
        self.page_home.view_library_clicked.connect(lambda: self.switch_page(1))
        self.page_home.view_progress_clicked.connect(lambda: self.switch_page(6))
        self.page_home.add_pose_clicked.connect(lambda: self.switch_page(7))

        self.page_library.pose_selected_for_practice.connect(self._on_start_practice_pose)
        self.page_recommendations.practice_pose_selected.connect(self._on_start_practice_pose)
        self.page_camera.back_to_library.connect(lambda: self.switch_page(1))
        self.page_add_pose.pose_saved.connect(lambda: self.switch_page(1))
        self.page_surya.finish_sequence.connect(lambda: self.switch_page(0))

    def _on_start_practice_pose(self, pose: Dict[str, Any]) -> None:
        self.page_camera.set_active_pose(pose)
        self.btn_nav_practice.setChecked(True)
        self.switch_page(3)

    def _on_logout(self) -> None:
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to log out from KI.AI?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.page_camera.stop_camera()
            self.page_surya.stop_camera()
            self.logout_requested.emit()

    def closeEvent(self, event) -> None:
        self.page_camera.stop_camera()
        self.page_surya.stop_camera()
        event.accept()
