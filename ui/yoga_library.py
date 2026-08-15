"""
Yoga Pose Library Screen for KI.AI — AI-Powered Yoga & Posture Intelligence.
Allows searching, filtering by difficulty/category/goal, viewing full pose details,
and launching live AI posture practice sessions.
Features pose-specific SVG figures in the top-right corner of each pose card.
"""

from typing import Any, Dict, List, Optional
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QCursor, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config import settings
from database.database import Database
from ui.pose_details import PoseDetailsDialog
from vision.reference_helper import ReferenceHelper


class PoseCard(QFrame):
    """
    Premium Yoga Pose Card matching target AI fitness design:
      - Top Image Area: Realistic studio yoga pose photo with subtle gradient
      - Top-Left: Difficulty badge pill (Beginner / Intermediate / Advanced)
      - Top-Right: Minimal anatomical reference figure in dark translucent box with emerald border
      - Pose title, Sanskrit / English subtitle
      - Goal tag with icon (🧘 Balance, 💪 Strength, etc.)
      - AI Detection Ready status indicator
      - Action footer: '▶ Practice Pose' + Bookmark '♡'
    """

    view_details = Signal(dict)
    start_practice = Signal(dict)

    def __init__(self, pose: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.pose = pose
        self.setProperty("class", "card")
        self.setMinimumHeight(370)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(f"""
            QFrame.card {{
                background-color: #131D2E;
                border: 1.5px solid #1E293B;
                border-radius: 14px;
                padding: 0px;
            }}
            QFrame.card:hover {{
                border: 1.5px solid {settings.THEME['primary']};
                background-color: #172338;
            }}
        """)
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # ==========================================
        # 1. TOP IMAGE AREA (Realistic Studio Photo)
        # ==========================================
        image_container = QFrame()
        image_container.setFixedHeight(155)
        image_container.setStyleSheet("""
            QFrame {
                background-color: #0B1120;
                border-radius: 10px;
                border: 1px solid #1E293B;
            }
        """)
        img_layout = QVBoxLayout(image_container)
        img_layout.setContentsMargins(8, 8, 8, 8)

        # Background Realistic Image
        self.lbl_bg_img = QLabel(image_container)
        self.lbl_bg_img.setGeometry(0, 0, 260, 155)
        self.lbl_bg_img.setScaledContents(True)
        self.lbl_bg_img.setStyleSheet("border-radius: 10px;")

        # Resolve image path
        img_path = self.pose.get("image_path", "")
        if not img_path or not Path(img_path).exists():
            clean_name = self.pose.get("name", "").lower().replace(" ", "_").replace("-", "_")
            fallback = Path("assets/images/yoga") / f"{clean_name}.png"
            img_path = str(fallback) if fallback.exists() else "assets/images/yoga/tadasana.png"

        pix = QPixmap(img_path)
        if not pix.isNull():
            self.lbl_bg_img.setPixmap(pix)

        # Overlay Row (Top-Left Badge + Top-Right Reference Figure)
        overlay_row = QHBoxLayout()
        overlay_row.setContentsMargins(0, 0, 0, 0)

        # TOP-LEFT: Difficulty Badge
        diff = self.pose.get("difficulty", "Beginner")
        diff_color = '#10B981' if diff == 'Beginner' else ('#38BDF8' if diff == 'Intermediate' else '#A855F7')
        diff_bg = 'rgba(6, 78, 59, 0.85)' if diff == 'Beginner' else ('rgba(14, 116, 144, 0.85)' if diff == 'Intermediate' else 'rgba(88, 28, 135, 0.85)')
        
        diff_badge = QLabel(diff)
        diff_badge.setStyleSheet(f"""
            background-color: {diff_bg};
            color: {diff_color};
            border: 1px solid {diff_color};
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.4px;
        """)
        overlay_row.addWidget(diff_badge, alignment=Qt.AlignTop | Qt.AlignLeft)
        overlay_row.addStretch()

        # TOP-RIGHT: Dedicated Anatomical Reference Figure Badge
        self.figure_badge = QLabel()
        self.figure_badge.setFixedSize(44, 44)
        self.figure_badge.setAlignment(Qt.AlignCenter)
        self.figure_badge.setToolTip(f"Anatomical Reference: {self.pose.get('name', 'Pose')}")
        self.figure_badge.setStyleSheet("""
            QLabel {
                background-color: rgba(15, 23, 42, 0.88);
                border: 1.5px solid #10B981;
                border-radius: 8px;
                padding: 2px;
            }
            QLabel:hover {
                border: 1.5px solid #34D399;
                background-color: rgba(6, 78, 59, 0.95);
            }
        """)

        fig_pix = ReferenceHelper.get_pose_figure_pixmap(self.pose, size=(36, 36))
        self.figure_badge.setPixmap(fig_pix)
        overlay_row.addWidget(self.figure_badge, alignment=Qt.AlignTop | Qt.AlignRight)

        img_layout.addLayout(overlay_row)
        img_layout.addStretch()

        layout.addWidget(image_container)

        # ==========================================
        # 2. CARD CONTENT
        # ==========================================
        # Pose Name
        name_lbl = QLabel(self.pose.get("name", "Pose"))
        name_lbl.setStyleSheet("font-size: 16px; font-weight: 800; color: #FFFFFF; margin-top: 2px;")
        layout.addWidget(name_lbl)

        # Sanskrit / English Subtitle
        sanskrit = self.pose.get("sanskrit_name", "")
        if sanskrit:
            s_lbl = QLabel(sanskrit)
            s_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-style: italic; font-weight: 500;")
            layout.addWidget(s_lbl)

        # Meta Row: Goal + AI Detection Ready Indicator
        meta_row = QHBoxLayout()
        meta_row.setSpacing(6)

        goal = self.pose.get("goal", "Balance")
        goal_icon = "🧘" if "Balance" in goal or "Flexibility" in goal else ("💪" if "Strength" in goal else "🌿")
        goal_tag = QLabel(f"{goal_icon} {goal}")
        goal_tag.setStyleSheet("background-color: #0F172A; border: 1px solid #334155; color: #38BDF8; border-radius: 4px; padding: 2px 6px; font-size: 10.5px; font-weight: 600;")
        meta_row.addWidget(goal_tag)

        ai_tag = QLabel("🟢 AI Ready")
        ai_tag.setStyleSheet("background-color: rgba(16, 185, 129, 0.12); border: 1px solid #10B981; color: #10B981; border-radius: 4px; padding: 2px 6px; font-size: 10px; font-weight: 700;")
        meta_row.addWidget(ai_tag)
        meta_row.addStretch()
        layout.addLayout(meta_row)

        # Short Description
        desc = self.pose.get("description", "")
        if len(desc) > 88:
            desc = desc[:85] + "..."
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; line-height: 1.25;")
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        layout.addStretch()

        # ==========================================
        # 3. ACTION FOOTER
        # ==========================================
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)

        btn_start = QPushButton("▶ Practice Pose")
        btn_start.setProperty("class", "btn_primary")
        btn_start.setFixedHeight(34)
        btn_start.clicked.connect(lambda: self.start_practice.emit(self.pose))
        btn_row.addWidget(btn_start, stretch=5)

        btn_save = QPushButton("♡")
        btn_save.setFixedSize(34, 34)
        btn_save.setToolTip("Save to favorites")
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0F172A;
                border: 1px solid #334155;
                color: #94A3B8;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 1px solid #10B981;
                color: #10B981;
                background-color: #1E293B;
            }
        """)
        btn_save.clicked.connect(lambda: btn_save.setText("♥" if btn_save.text() == "♡" else "♡"))
        btn_row.addWidget(btn_save, stretch=1)

        layout.addLayout(btn_row)

    def mousePressEvent(self, event) -> None:
        """Clicking on the card opens full pose details dialog."""
        if event.button() == Qt.LeftButton:
            self.view_details.emit(self.pose)


class YogaLibrary(QWidget):
    """Searchable and filterable catalog of all yoga poses with dynamic pose figures."""

    pose_selected_for_practice = Signal(dict)

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.all_poses: List[Dict[str, Any]] = []
        self.view_mode = "grid"
        self._init_ui()
        self.load_poses()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(14)

        # Top Header
        title_box = QVBoxLayout()
        title_lbl = QLabel("🧘 Yoga Library")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: 800; color: #FFFFFF;")
        title_box.addWidget(title_lbl)

        sub_lbl = QLabel("Browse poses with verified anatomical angle rules and real-time AI posture feedback.")
        sub_lbl.setStyleSheet(f"color: {settings.THEME['text_secondary']}; font-size: 12.5px;")
        title_box.addWidget(sub_lbl)
        main_layout.addLayout(title_box)

        # Filter and Search Toolbar
        filter_card = QFrame()
        filter_card.setProperty("class", "card")
        filter_card.setStyleSheet("background-color: #111827; border: 1px solid #1E293B; border-radius: 10px; padding: 6px;")
        f_layout = QHBoxLayout(filter_card)
        f_layout.setContentsMargins(8, 6, 8, 6)
        f_layout.setSpacing(8)

        # Search Box
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍  Search poses...")
        self.txt_search.setFixedHeight(34)
        self.txt_search.textChanged.connect(self.filter_poses)
        f_layout.addWidget(self.txt_search, stretch=3)

        # Category Filter
        self.combo_category = QComboBox()
        self.combo_category.addItem("All Categories")
        self.combo_category.addItems(settings.CATEGORIES)
        self.combo_category.setFixedHeight(34)
        self.combo_category.currentIndexChanged.connect(self.filter_poses)
        f_layout.addWidget(self.combo_category, stretch=2)

        # Difficulty Filter
        self.combo_difficulty = QComboBox()
        self.combo_difficulty.addItem("All Difficulty")
        self.combo_difficulty.addItems(settings.DIFFICULTY_LEVELS)
        self.combo_difficulty.setFixedHeight(34)
        self.combo_difficulty.currentIndexChanged.connect(self.filter_poses)
        f_layout.addWidget(self.combo_difficulty, stretch=2)

        # Goal Filter
        self.combo_goal = QComboBox()
        self.combo_goal.addItem("All Goals")
        self.combo_goal.addItems(settings.GOALS)
        self.combo_goal.setFixedHeight(34)
        self.combo_goal.currentIndexChanged.connect(self.filter_poses)
        f_layout.addWidget(self.combo_goal, stretch=2)

        # Sort Dropdown
        self.combo_sort = QComboBox()
        self.combo_sort.addItems(["Sort: A–Z", "Sort: Difficulty", "Sort: Hold Duration"])
        self.combo_sort.setFixedHeight(34)
        self.combo_sort.currentIndexChanged.connect(self.filter_poses)
        f_layout.addWidget(self.combo_sort, stretch=2)

        # Grid / List Toggle
        self.btn_grid_mode = QPushButton("▦ Grid")
        self.btn_grid_mode.setCheckable(True)
        self.btn_grid_mode.setChecked(True)
        self.btn_grid_mode.setFixedHeight(34)
        self.btn_grid_mode.setStyleSheet("""
            QPushButton { background-color: #064E3B; color: #10B981; border: 1px solid #10B981; border-radius: 6px; padding: 4px 10px; font-weight: bold; }
        """)
        self.btn_grid_mode.clicked.connect(self._toggle_grid_mode)
        f_layout.addWidget(self.btn_grid_mode)

        main_layout.addWidget(filter_card)

        # Poses Grid Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 4, 0, 4)
        self.grid_layout.setSpacing(14)

        scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(scroll_area)

    def _toggle_grid_mode(self) -> None:
        if self.btn_grid_mode.text() == "▦ Grid":
            self.btn_grid_mode.setText("☷ List")
            self.view_mode = "list"
        else:
            self.btn_grid_mode.setText("▦ Grid")
            self.view_mode = "grid"
        self.filter_poses()

    def load_poses(self) -> None:
        self.all_poses = self.db.get_all_poses()
        self.filter_poses()

    def filter_poses(self) -> None:
        # Clear existing grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        search_text = self.txt_search.text().strip().lower()
        selected_cat = self.combo_category.currentText()
        selected_diff = self.combo_difficulty.currentText()
        selected_goal = self.combo_goal.currentText()
        sort_mode = self.combo_sort.currentText()

        filtered = []
        for p in self.all_poses:
            if p.get("category") == "Surya Namaskar" and selected_cat != "Surya Namaskar" and not search_text:
                continue

            if search_text:
                name_match = search_text in p.get("name", "").lower()
                sanskrit_match = search_text in p.get("sanskrit_name", "").lower()
                desc_match = search_text in p.get("description", "").lower()
                if not (name_match or sanskrit_match or desc_match):
                    continue

            if selected_cat != "All Categories" and p.get("category") != selected_cat:
                continue
            if selected_diff != "All Difficulty" and p.get("difficulty") != selected_diff:
                continue
            if selected_goal != "All Goals" and p.get("goal") != selected_goal:
                continue

            filtered.append(p)

        # Sorting
        if sort_mode == "Sort: A–Z":
            filtered.sort(key=lambda x: x.get("name", "").lower())
        elif sort_mode == "Sort: Difficulty":
            diff_order = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}
            filtered.sort(key=lambda x: diff_order.get(x.get("difficulty", "Beginner"), 1))
        elif sort_mode == "Sort: Hold Duration":
            filtered.sort(key=lambda x: x.get("hold_duration", 20), reverse=True)

        columns = 1 if self.view_mode == "list" else 4
        for idx, pose in enumerate(filtered):
            card = PoseCard(pose)
            card.view_details.connect(self._on_view_details)
            card.start_practice.connect(self._on_start_practice)
            row = idx // columns
            col = idx % columns
            self.grid_layout.addWidget(card, row, col)

        if not filtered:
            lbl_empty = QLabel("No yoga poses match the selected filters.")
            lbl_empty.setStyleSheet("color: #64748B; font-size: 14px; padding: 40px;")
            lbl_empty.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(lbl_empty, 0, 0, 1, columns)

    def _on_view_details(self, pose: Dict[str, Any]) -> None:
        dialog = PoseDetailsDialog(pose, parent=self)
        dialog.start_practice_clicked.connect(self._on_start_practice)
        dialog.exec()

    def _on_start_practice(self, pose: Dict[str, Any]) -> None:
        self.pose_selected_for_practice.emit(pose)
