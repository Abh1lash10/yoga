# AI-Based Yoga Pose Recommendation and Real-Time Posture Correction Using Computer Vision

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-green.svg)](https://www.qt.io/qt-for-python)
[![Computer Vision](https://img.shields.io/badge/Vision-OpenCV%20%7C%20MediaPipe-orange.svg)](https://developers.google.com/mediapipe)
[![Tests](https://img.shields.io/badge/Tests-PyTest%20(22%20Passed)-brightgreen.svg)](https://docs.pytest.org/)
[![Database](https://img.shields.io/badge/Database-SQLite3-lightgrey.svg)](https://www.sqlite.org/)

---

## 1. Project Title
**AI-Based Yoga Pose Recommendation and Real-Time Posture Correction Using Computer Vision**

---

## 2. Project Overview
The **AI Yoga Assistant** is a desktop-based intelligent fitness application built in Python that combines real-time webcam video processing, MediaPipe 33-landmark pose estimation, trigonometric joint-angle vector analysis, rule-based pose classification, goal-oriented recommendation logic, and an embedded SQLite database.

The application allows users to practice yoga poses in front of a laptop or USB webcam, receives instant visual and verbal posture corrections, tracks posture accuracy scores (0–100%), times steady posture holds, records practice session history, visualizes improvement analytics via Matplotlib, and creates custom user-defined yoga poses using live multi-frame reference capture.

---

## 3. Problem Statement
Traditional digital yoga applications provide static instructional images or pre-recorded videos. However:
1. They lack **real-time posture assessment** to detect when a practitioner's knee, hip, or shoulder is misaligned.
2. Practicing with improper posture can lead to muscle strain, joint hyperextension, or reduced effectiveness.
3. Hiring private yoga instructors for every practice session is cost-prohibitive for many practitioners.

This project bridges that gap by providing an automated, private, offline AI coach that identifies misalignments in real time and offers targeted corrective guidance.

---

## 4. Key Objectives
- **Real-Time Landmark Detection**: Track 33 anatomical body keypoints at ~30 FPS with confidence and visibility validation.
- **Trigonometric Posture Analysis**: Calculate precise 2D/3D interior joint angles at elbows, knees, hips, and shoulders.
- **Rule-Based Posture Scoring**: Compute weighted accuracy scores (0–100%) and classify postures into intuitive quality tiers (Excellent, Good, Needs Improvement, Incorrect).
- **Actionable Corrective Coaching**: Generate natural language corrective cues (e.g., *"Bend your left knee 15° more"*) with optional voice feedback.
- **Personalized Recommendations**: Suggest poses tailored to user goals (Flexibility, Strength, Balance, Relaxation, General Fitness) and target historical weak spots.
- **Custom Pose Creation**: Enable practitioners to record new yoga poses via live webcam reference capture without modifying code.

---

## 5. Core Features
1. **User Profile & Auth**: Profile creation with age, experience level (Beginner/Intermediate/Advanced), and primary fitness goals.
2. **Interactive Home Dashboard**: Summary metrics (Average Score, Best Score, Total Sessions), daily routine card, and recent workouts.
3. **Searchable Yoga Library**: Filter by Category (Standing, Sitting, Balance, Strength, Flexibility, Relaxation, Custom), Difficulty, and Goal.
4. **Detailed Pose Viewer**: Step-by-step numbered instructions, health benefits, safety precautions, and target joint angle summaries.
5. **Camera Setup & Body Visibility Check**: Verifies distance (2–3 meters) and landmark visibility before scoring to eliminate false readings.
6. **Visual Skeleton Overlay**: High-contrast, color-coded skeleton (Green = Correct, Yellow = Close, Red = Incorrect) with live angle tags.
7. **Pose Identification**: Distinguishes between selected pose and performed pose (e.g., alerts if user performs Mountain Pose during Warrior II).
8. **Hold Timer with Auto-Pause**: Requires $\ge 80\%$ accuracy to count down hold duration; automatically pauses if alignment deviates.
9. **Post-Session Summary Dialog**: Granular breakdown of average score, hold time, corrections count, and personalized improvement tips.
10. **Matplotlib Analytics Dashboard**: Score progression line charts over time and pose-by-pose average accuracy comparisons.
11. **Custom Pose Wizard**: Multi-frame (30-frame) stability capture, automated angle averaging, variance-based tolerance calculation, and tolerance adjustment sliders.
12. **Voice Coach Integration**: Thread-safe offline text-to-speech with cooldown timers to avoid audio overlap.

---

## 6. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Language** | Python 3.12+ / 3.13 | Core application language |
| **GUI Framework** | PySide6 (Qt 6) | Modern desktop UI, QThreads, and layouts |
| **Computer Vision** | OpenCV (`opencv-python`) | Webcam stream handling and image rendering |
| **Pose Estimation** | MediaPipe Tasks Vision API | 33 3D full-body landmark detection |
| **Numerical Processing** | NumPy | Vector trigonometry and coordinate normalization |
| **Database** | SQLite3 | Relational database storage |
| **Data Visualization** | Matplotlib | Score history trend lines and bar charts |
| **Voice Feedback** | pyttsx3 | Offline text-to-speech coaching |
| **Testing** | pytest | Automated unit test suite |

---

## 7. System Architecture

```
+-----------------------------------------------------------------------------------+
|                                 CORE PIPELINE FLOW                                |
+-----------------------------------------------------------------------------------+
  WEBCAM (OpenCV Capture @ 30 FPS)
     ↓
  RGB VIDEO FRAME
     ↓
  POSE LANDMARK ESTIMATION (MediaPipe Tasks Vision API / 33 3D Keypoints)
     ↓
  BODY VISIBILITY & CONFIDENCE VERIFICATION (Keypoint presence check)
     ↓
  GEOMETRIC FEATURE EXTRACTION (2D/3D Joint Vector Angle Calculation)
     ↓
  ┌─────────────────────────────────────────────────────────────┐
  │  POSE IDENTIFICATION          │  POSTURE COMPARISON &       │
  │  (Classification vs Library)  │  DEVIATION ANALYSIS (Rules) │
  └───────────────────────────────┴─────────────────────────────┘
     ↓                                  ↓
  DETECTED POSE CONFIRMATION         ACCURACY SCORE & LEVEL (0-100%)
     ↓                                  ↓
  HOLD TIMER MANAGEMENT (Auto-pause) ACTIONABLE CORRECTIVE COACHING
     ↓                                  ↓
  SESSION PERSISTENCE (SQLite Database / History & Feedback Logs)
     ↓
  PROGRESS ANALYTICS & PERSONALIZED RECOMMENDATIONS (Goal/Weakness-Based)
```

---

## 8. Installation & Setup

### Prerequisites
- Python 3.12 or 3.13 installed on Windows, macOS, or Linux.
- Webcam (built-in laptop camera or external USB camera).

### 1. Clone or Open Workspace
```bash
cd AI-YOGA
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 9. Project Directory Structure

```
AI-YOGA/
├── app.py                      # Main application entry point
├── requirements.txt            # Package dependencies
├── .gitignore                  # Git exclusions
│
├── config/
│   ├── __init__.py
│   └── settings.py             # Centralized constants, paths, thresholds, and theme tokens
│
├── database/
│   ├── __init__.py
│   ├── database.py             # SQLite helper with CRUD operations and seeding
│   ├── schema.sql              # Relational database schema with foreign keys
│   └── yoga.db                 # SQLite database file
│
├── vision/
│   ├── __init__.py
│   ├── camera.py               # Asynchronous QThread camera worker
│   ├── pose_detector.py        # MediaPipe Pose Landmarker detector
│   ├── landmarks.py            # Landmark mappings, skeleton pairs, and visibility check
│   └── drawing.py              # Visual skeleton rendering and posture color coding
│
├── analysis/
│   ├── __init__.py
│   ├── angle_calculator.py     # 2D/3D vector angle calculation at joint vertices
│   ├── pose_classifier.py      # Rule-based pose identification engine
│   ├── posture_checker.py      # Posture accuracy and deviation analyzer
│   ├── score_calculator.py     # Weighted score calculator & qualitative tiers
│   └── feedback.py             # Directional feedback generator & voice synthesis
│
├── recommendation/
│   ├── __init__.py
│   └── recommender.py          # Recommendation engine (goals, history, weakness)
│
├── ui/
│   ├── __init__.py
│   ├── styles.py               # Modern dark theme QSS stylesheet
│   ├── main_window.py          # Sidebar navigation shell and view orchestrator
│   ├── login_window.py         # Profile switcher & user registration dialog
│   ├── home_window.py          # Home dashboard with metrics & recommendations
│   ├── yoga_library.py         # Searchable yoga pose catalog with filters
│   ├── pose_details.py         # Detailed pose modal with instructions & benefits
│   ├── camera_window.py        # Live practice screen, HUD overlays, and hold timer
│   ├── recommendation_window.py# Dedicated personalized recommendations page
│   ├── add_pose_window.py      # Custom pose creation wizard with multi-frame capture
│   ├── progress_window.py      # Matplotlib analytics (trends & pose comparisons)
│   └── session_summary.py      # Post-practice summary & actionable coaching tips
│
├── data/
│   ├── poses.json              # 12 Initial validated yoga poses with full rules
│   └── reference_poses/        # Storage for captured custom pose snapshots
│
├── models/
│   └── pose_landmarker.task    # Official MediaPipe Pose Landmarker model
│
├── tests/
│   ├── test_angles.py          # Unit tests for trigonometric calculations
│   ├── test_scoring.py         # Unit tests for posture scoring & tiers
│   ├── test_pose_rules.py      # Unit tests for posture checker & classification
│   ├── test_recommendation.py  # Unit tests for recommendation algorithms
│   └── test_database.py        # Unit tests for SQLite DB operations & persistence
│
└── docs/
    ├── architecture.md         # System architecture & threading model
    ├── algorithms.md           # Mathematical formulas & algorithms
    └── database.md             # Entity-Relationship diagram & schema specs
```

---

## 10. Initial Yoga Pose Dataset (12 Validated Poses)

1. **Tadasana (Mountain Pose)** — Standing / Balance
2. **Virabhadrasana II (Warrior II)** — Standing / Strength
3. **Vrikshasana (Tree Pose)** — Balance & Focus
4. **Trikonasana (Triangle Pose)** — Standing / Flexibility
5. **Utkatasana (Chair Pose)** — Strength & Stamina
6. **Bhujangasana (Cobra Pose)** — Spine Flexibility
7. **Balasana (Child's Pose)** — Relaxation & Restoration
8. **Adho Mukha Svanasana (Downward-Facing Dog)** — Strength / General Fitness
9. **Setu Bandhasana (Bridge Pose)** — Glute & Spine Strength
10. **Dhanurasana (Bow Pose)** — Backbend Flexibility
11. **Natarajasana (Dancer Pose)** — Advanced Balance & Flexibility
12. **Sukhasana (Easy Pose)** — Seated Meditation / Relaxation

---

## 11. How the AI Works

### 1. Landmark Estimation
The camera captures frames at 30 FPS. MediaPipe processes each frame to extract 33 3D landmark coordinates $(x, y, z)$ with presence and visibility probabilities.

### 2. Geometric Angle Calculation
For any joint $B$ connected to landmarks $A$ and $C$:
$$\vec{u} = \vec{BA}, \quad \vec{v} = \vec{BC}$$
$$\theta = \arccos\left(\frac{\vec{u} \cdot \vec{v}}{\|\vec{u}\| \|\vec{v}\|}\right) \times \left(\frac{180^\circ}{\pi}\right)$$

### 3. Posture Evaluation & Scoring
For target angle $\theta_{target}$ with tolerance $\delta$:
$$\Delta = |\theta_{actual} - \theta_{target}|$$
$$S_i = \begin{cases} 100 - (\frac{\Delta}{\delta} \times 10), & \text{if } \Delta \le \delta \\ \max(0, 90 - \frac{\Delta - \delta}{45^\circ} \times 90), & \text{if } \Delta > \delta \end{cases}$$
$$\text{Overall Score} = \frac{\sum S_i \cdot w_i}{\sum w_i}$$

---

## 12. Running Unit Tests

Run the full automated test suite using `pytest`:
```bash
pytest tests/ -v
```

Expected Output:
```
tests/test_angles.py::test_calculate_right_angle PASSED
tests/test_angles.py::test_calculate_straight_line_angle PASSED
tests/test_angles.py::test_calculate_acute_angle PASSED
tests/test_angles.py::test_zero_length_vector_handling PASSED
tests/test_angles.py::test_calculate_angle_with_vertical PASSED
tests/test_angles.py::test_calculate_angle_with_horizontal PASSED
tests/test_angles.py::test_extract_all_angles_from_landmarks PASSED
tests/test_database.py::test_user_creation_and_retrieval PASSED
tests/test_database.py::test_seed_poses_loaded PASSED
tests/test_database.py::test_add_custom_pose_and_template PASSED
tests/test_database.py::test_session_saving_and_analytics PASSED
tests/test_pose_rules.py::test_tadasana_correct_evaluation PASSED
tests/test_pose_rules.py::test_warrior2_incorrect_knee_feedback PASSED
tests/test_pose_rules.py::test_pose_classifier_distinguishes_tadasana_vs_warrior PASSED
tests/test_recommendation.py::test_goal_based_recommendations PASSED
tests/test_recommendation.py::test_weakness_targeted_practice_recommendation PASSED
tests/test_scoring.py::test_joint_score_exact_target PASSED
tests/test_scoring.py::test_joint_score_within_tolerance PASSED
tests/test_scoring.py::test_joint_score_at_tolerance_boundary PASSED
tests/test_scoring.py::test_joint_score_beyond_tolerance_decay PASSED
tests/test_scoring.py::test_overall_weighted_score PASSED
tests/test_scoring.py::test_score_level_boundaries PASSED

============================== 22 passed in 1.6s ==============================
```

---

## 13. How to Launch the Application

### Option A: Native Desktop Application (PySide6 GUI)
```bash
python app.py
```
*Features split-screen Login/Signup, Emerald Dark Theme, 12-Step Surya Yoga flow, Reference Assist, and local webcam analysis.*

### Option B: Web Application (Browser & Mobile Access)
```bash
python web_app.py
```
*Accessible locally on `http://localhost:8080` and over local Wi-Fi / hotspot on `http://192.168.1.5:8080`.*

---

## 14. Demonstration Walkthrough Scenario

1. **Launch**: Run `python app.py`. The modern dark-themed interface opens on the Home Dashboard.
2. **User Profile**: Click "Switch Profile" on the lower sidebar to select or register a user (e.g., Alice, Goal: Flexibility, Level: Beginner).
3. **Explore Library**: Navigate to **Yoga Library**, search for "Warrior", or filter by category "Standing".
4. **View Pose Details**: Click "Details" on Warrior II to view instructions, health benefits, and precautions.
5. **Start Practice**: Click "Practice 🎥".
6. **Live Camera & Skeleton**: The webcam opens in a dedicated thread. Stand 2–3 meters away. The visual skeleton turns green/yellow/red in real time.
7. **Perform Pose & Observe Feedback**:
   - Perform Warrior II with a straight front knee: The HUD indicates score ~70% and advises: *"Bend your front left knee deeper toward 90 degrees"*.
   - Bend your front knee properly: The skeleton turns green, the score rises above 90%, and the Hold Timer begins ticking (`01 / 20 sec`).
8. **Hold Completion**: Hold steady for 20 seconds. The system announces completion and opens the **Session Summary Dialog**.
9. **View Analytics**: Open **Progress & Analytics** to observe your session score trend and pose accuracy bars.
10. **Create Custom Pose**: Navigate to **Custom Poses**, fill in metadata, perform your new posture in front of the camera, and click "Capture Reference Pose". The system samples 30 frames, calculates mean joint angles, and saves the custom pose for instant practice.

---

## 15. Privacy & Security
- **100% Local Processing**: All computer vision and pose landmark calculations run entirely on the local CPU without external cloud APIs.
- **No Video Uploads**: Video frames are processed in-memory and are never stored or transmitted.

---

## 16. Safety Disclaimer
> **Disclaimer**: This application provides general fitness guidance and is not a medical diagnostic system. Always perform yoga within a comfortable range of motion and stop immediately if you experience pain, dizziness, or physical discomfort.
