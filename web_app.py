"""
KI.AI Web Application Server.
AI-Powered Yoga & Posture Intelligence.
Serves full browser interface on port 8080 with real-time pose checking,
Surya Yoga sequence, user authentication, and SQLite persistence.
"""

import json
import logging
import os
import socket
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_cors import CORS

from analysis.angle_calculator import AngleCalculator
from analysis.feedback import FeedbackEngine
from analysis.pose_classifier import PoseClassifier
from analysis.posture_checker import PostureChecker
from analysis.score_calculator import ScoreCalculator
from config import settings
from database.database import Database
from recommendation.recommender import PoseRecommender

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates")
CORS(app)

db = Database()
posture_checker = PostureChecker()
recommender = PoseRecommender(db)
all_poses_cache = db.get_all_poses()


def get_local_ip() -> str:
    """Gets local IP address on Wi-Fi/LAN."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


@app.route("/")
def index():
    """Renders the main KI.AI web application."""
    return render_template("index.html")


@app.route("/admin")
def admin_console():
    """Renders the KI.AI Admin Console & Posture Intelligence Operations Center."""
    return render_template("admin.html")


@app.route("/assets/<path:filename>")
def serve_assets(filename):
    """Serves static assets including SVG pose figures and images."""
    return send_from_directory(str(Path("assets").resolve()), filename)


@app.route("/api/poses", methods=["GET"])
def get_poses():
    """Returns all yoga poses with rules."""
    poses = db.get_all_poses()
    return jsonify(poses)


@app.route("/api/surya", methods=["GET"])
def get_surya_poses():
    """Returns 12-step Surya Namaskar sequence."""
    surya = db.get_surya_namaskar_poses()
    return jsonify(surya)


@app.route("/api/login", methods=["POST"])
def login():
    """Authenticates user with email and password."""
    data = request.json or {}
    email = data.get("email", "")
    password = data.get("password", "")

    success, msg, user = db.authenticate_user(email, password)
    if success and user:
        return jsonify({"status": "success", "message": msg, "user": user})
    return jsonify({"status": "error", "message": msg}), 401


@app.route("/api/register", methods=["POST"])
def register():
    """Registers a new user profile."""
    data = request.json or {}
    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")
    age = int(data.get("age", 25))
    experience = data.get("experience", "Beginner")
    goal = data.get("goal", "General Fitness")

    success, msg, user = db.register_user(
        name=name,
        email=email,
        password=password,
        age=age,
        experience=experience,
        goal=goal,
    )

    if success:
        return jsonify({"status": "success", "message": msg, "user": user})
    return jsonify({"status": "error", "message": msg}), 400


@app.route("/api/analyze_posture", methods=["POST"])
def analyze_posture():
    """
    Receives landmark coordinates from browser camera, extracts joint angles,
    evaluates posture against target rules, and returns 4-color status dots (🟢 🔴 🟡 ⚪)
    and directional coaching feedback.
    """
    data = request.json or {}
    landmarks_raw = data.get("landmarks", {})
    pose_id = data.get("pose_id")

    if not landmarks_raw or not pose_id:
        return jsonify({"status": "error", "message": "Missing landmarks or pose_id"}), 400

    target_pose = db.get_pose_by_id(int(pose_id))
    if not target_pose:
        return jsonify({"status": "error", "message": "Pose not found"}), 404

    # Normalize landmarks into dictionary expected by AngleCalculator
    # Format: {"LEFT_KNEE": {"x": 0.5, "y": 0.8, "z": 0.0, "visibility": 0.9}, ...}
    landmarks = {}
    for name, lm in landmarks_raw.items():
        landmarks[name] = {
            "x": float(lm.get("x", 0.0)),
            "y": float(lm.get("y", 0.0)),
            "z": float(lm.get("z", 0.0)),
            "visibility": float(lm.get("visibility", 0.9)),
            "px": int(lm.get("x", 0.0) * 640),
            "py": int(lm.get("y", 0.0) * 480),
        }

    # Extract 2D/3D angles
    actual_angles = AngleCalculator.extract_all_angles(landmarks)

    # Pose Classification
    detected_name, match_score, _ = PoseClassifier.identify_pose(actual_angles, all_poses_cache)

    # Posture Evaluation & Scoring
    posture_result = posture_checker.check_posture(target_pose, actual_angles, is_body_visible=True)

    return jsonify({
        "status": "success",
        "detected_pose": detected_name,
        "match_score": round(match_score, 1),
        "overall_score": round(posture_result.get("overall_score", 0.0), 1),
        "score_level": posture_result.get("score_level", "INCORRECT"),
        "level_info": posture_result.get("level_info", settings.SCORE_LEVELS["INCORRECT"]),
        "joint_results": posture_result.get("joint_results", []),
        "primary_feedback": posture_result.get("primary_feedback", ""),
        "structured_feedback": posture_result.get("structured_feedback", []),
        "actual_angles": {k: round(v, 1) for k, v in actual_angles.items()},
    })


@app.route("/api/save_session", methods=["POST"])
def save_session():
    """Saves completed practice session into SQLite."""
    data = request.json or {}
    user_id = data.get("user_id", 1)
    pose_id = data.get("pose_id", 1)
    duration = int(data.get("duration", 0))
    avg_score = float(data.get("average_score", 0.0))
    final_score = float(data.get("final_score", 0.0))
    hold_duration = int(data.get("hold_duration", 0))
    corrections_count = int(data.get("corrections_count", 0))

    session_id = db.save_practice_session(
        user_id=user_id,
        pose_id=pose_id,
        duration=duration,
        average_score=avg_score,
        final_score=final_score,
        hold_duration=hold_duration,
        corrections_count=corrections_count,
    )

    return jsonify({"status": "success", "session_id": session_id})


@app.route("/api/history/<int:user_id>", methods=["GET"])
def get_history(user_id):
    """Returns practice history for user."""
    pose_filter = request.args.get("pose")
    min_score = request.args.get("min_score", type=float)
    history = db.get_all_practice_history(user_id, pose_filter=pose_filter, min_score=min_score)
    return jsonify(history)


@app.route("/api/stats/<int:user_id>", methods=["GET"])
def get_stats(user_id):
    """Returns lifetime metrics and progress breakdown."""
    stats = db.get_user_stats(user_id)
    progression = db.get_analytics_score_progression(user_id)
    pose_breakdown = db.get_pose_performance_breakdown(user_id)
    return jsonify({
        "stats": stats,
        "progression": progression,
        "pose_breakdown": pose_breakdown,
    })


@app.route("/api/recommendations/<int:user_id>", methods=["GET"])
def get_recommendations(user_id):
    """Returns personalized recommendation feed."""
    recs = recommender.get_recommendations(user_id)
    return jsonify(recs)


if __name__ == "__main__":
    local_ip = get_local_ip()
    port = int(os.environ.get("PORT", 8080))

    print("=" * 65)
    print("   [KI.AI] AI-Powered Yoga & Posture Intelligence")
    print("=" * 65)
    print(f"   * Local URL:             http://localhost:{port}")
    print(f"   * Shareable Network URL: http://{local_ip}:{port}")
    print("   * Default Demo Account:  abhilash@ki.ai  (Password: password123)")
    print("=" * 65)

    app.run(host="0.0.0.0", port=port, debug=False)
