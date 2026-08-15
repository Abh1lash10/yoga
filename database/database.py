"""
Database Manager for KI.AI — AI-Powered Yoga & Posture Intelligence.
Provides thread-safe SQLite operations, automated schema initialization,
user authentication, profile management, JSON pose seeding, and full CRUD helpers.
"""

import hashlib
import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from config import settings

logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Generates a secure SHA-256 hash for user passwords."""
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


class Database:
    """Manages SQLite database connections, authentication, and operations."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_PATH
        self.schema_path = settings.SCHEMA_PATH
        self.init_db()
        self.seed_initial_poses()
        self.seed_surya_namaskar_poses()
        self.seed_default_users()

    @contextmanager
    def get_connection(self):
        """Context manager for SQLite database connection."""
        conn = sqlite3.connect(str(self.db_path), timeout=20.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error during transaction: {e}")
            raise
        finally:
            conn.close()

    def init_db(self) -> None:
        """Initializes tables using schema.sql and handles column migrations."""
        try:
            if not self.schema_path.exists():
                logger.error(f"Schema file not found at {self.schema_path}")
                return

            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Check if users table exists and migrate columns first
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
                if cursor.fetchone():
                    cursor.execute("PRAGMA table_info(users);")
                    columns = [row["name"] for row in cursor.fetchall()]
                    if "email" not in columns:
                        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT DEFAULT '';")
                    if "password_hash" not in columns:
                        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT DEFAULT '';")
                    if "avatar_url" not in columns:
                        cursor.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT '';")

                # Check if poses table exists and migrate figure_path column
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='poses';")
                if cursor.fetchone():
                    cursor.execute("PRAGMA table_info(poses);")
                    p_cols = [row["name"] for row in cursor.fetchall()]
                    if "figure_path" not in p_cols:
                        cursor.execute("ALTER TABLE poses ADD COLUMN figure_path TEXT DEFAULT '';")

            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema_sql = f.read()

            with self.get_connection() as conn:
                conn.executescript(schema_sql)

            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    # ==========================================
    # User Authentication & Profile Methods
    # ==========================================

    def seed_default_users(self) -> None:
        """Seeds default user accounts and repairs any users with empty credentials."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                default_pw = hash_password("password123")
                guest_pw = hash_password("guest123")

                # Repair ID 1 if email or password_hash is empty
                cursor.execute(
                    """
                    UPDATE users 
                    SET email = 'abhilash@ki.ai', password_hash = ?, name = 'Abhilash'
                    WHERE (email IS NULL OR email = '' OR password_hash IS NULL OR password_hash = '') AND id = 1;
                    """,
                    (default_pw,),
                )

                # Ensure abhilash@ki.ai exists
                cursor.execute("SELECT id FROM users WHERE LOWER(email) = 'abhilash@ki.ai';")
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        INSERT INTO users (name, email, password_hash, age, experience, goal)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        ("Abhilash", "abhilash@ki.ai", default_pw, 23, "Intermediate", "General Fitness"),
                    )

                # Ensure guest@ki.ai exists
                cursor.execute("SELECT id FROM users WHERE LOWER(email) = 'guest@ki.ai';")
                if not cursor.fetchone():
                    cursor.execute(
                        """
                        INSERT INTO users (name, email, password_hash, age, experience, goal)
                        VALUES (?, ?, ?, ?, ?, ?);
                        """,
                        ("Guest User", "guest@ki.ai", guest_pw, 25, "Beginner", "Flexibility"),
                    )

                logger.info("Default users seeded and validated successfully.")
        except Exception as e:
            logger.error(f"Failed to seed default users: {e}")

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Retrieves all registered user profiles."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, age, experience, goal, created_at FROM users ORDER BY id ASC;")
            return [dict(r) for r in cursor.fetchall()]

    def create_user(
        self,
        name: str,
        age: int = 25,
        experience: str = "Beginner",
        goal: str = "General Fitness",
        email: Optional[str] = None,
        password: str = "password123",
    ) -> int:
        """Helper to create a user and return user ID directly."""
        email_clean = (email or f"{name.lower().replace(' ', '')}{int(datetime.now().timestamp())}@ki.ai").strip().lower()
        pw_hash = hash_password(password)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash, age, experience, goal)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (name.strip(), email_clean, pw_hash, age, experience, goal),
            )
            return cursor.lastrowid

    def get_pose_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves a yoga pose and its rules by name or Sanskrit name."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM poses 
                WHERE LOWER(name) = LOWER(?) OR LOWER(sanskrit_name) = LOWER(?);
                """,
                (name.strip(), name.strip()),
            )
            row = cursor.fetchone()
            if not row:
                return None

            pose_dict = dict(row)
            cursor.execute("SELECT joint_name, target_angle, min_angle, max_angle, tolerance, weight, feedback_message FROM pose_rules WHERE pose_id = ?;", (pose_dict["id"],))
            pose_dict["rules"] = [dict(r) for r in cursor.fetchall()]
            try:
                pose_dict["benefits"] = json.loads(pose_dict["benefits"]) if pose_dict["benefits"] else []
            except Exception:
                pass
            try:
                pose_dict["instructions"] = json.loads(pose_dict["instructions"]) if pose_dict["instructions"] else []
            except Exception:
                pass
            return pose_dict

    def register_user(
        self,
        name: str,
        email: str,
        password: str,
        age: int = 25,
        experience: str = "Beginner",
        goal: str = "General Fitness",
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Registers a new user in the SQLite database.
        
        Returns:
            Tuple of (success: bool, message: str, user_dict: Optional[dict])
        """
        email_clean = email.strip().lower()
        name_clean = name.strip()

        if not name_clean:
            return False, "Full Name is required.", None
        if not email_clean or "@" not in email_clean:
            return False, "A valid email address is required.", None
        if len(password) < 6:
            return False, "Password must be at least 6 characters.", None

        pw_hash = hash_password(password)

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?;", (email_clean,))
                if cursor.fetchone():
                    return False, "An account with this email already exists.", None

                cursor.execute(
                    """
                    INSERT INTO users (name, email, password_hash, age, experience, goal)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (name_clean, email_clean, pw_hash, age, experience, goal),
                )
                user_id = cursor.lastrowid
                user = self.get_user_by_id(user_id)
                return True, "Account created successfully.", user
        except Exception as e:
            logger.error(f"Error registering user {email}: {e}")
            return False, "Failed to create account due to database error.", None

    def authenticate_user(self, email: str, password: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Authenticates a user via email and password.
        
        Returns:
            Tuple of (success: bool, message: str, user_dict: Optional[dict])
        """
        email_clean = email.strip().lower()
        pw_hash = hash_password(password)

        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, name, email, password_hash, age, experience, goal, created_at
                    FROM users
                    WHERE LOWER(email) = ?;
                    """,
                    (email_clean,),
                )
                row = cursor.fetchone()
                if not row:
                    return False, "No account found with this email address.", None

                if row["password_hash"] != pw_hash:
                    return False, "Incorrect password. Please try again.", None

                user_dict = dict(row)
                del user_dict["password_hash"]
                return True, f"Welcome back, {user_dict['name']}!", user_dict
        except Exception as e:
            logger.error(f"Authentication error for {email}: {e}")
            return False, "Authentication service error. Please try again.", None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a user profile by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, age, experience, goal, created_at FROM users WHERE id = ?;", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Retrieves a user profile by email."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, email, age, experience, goal, created_at FROM users WHERE LOWER(email) = ?;", (email.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_user_profile(
        self,
        user_id: int,
        name: Optional[str] = None,
        age: Optional[int] = None,
        experience: Optional[str] = None,
        goal: Optional[str] = None,
    ) -> bool:
        """Updates user profile settings."""
        fields = []
        params = []
        if name is not None:
            fields.append("name = ?")
            params.append(name.strip())
        if age is not None:
            fields.append("age = ?")
            params.append(age)
        if experience is not None:
            fields.append("experience = ?")
            params.append(experience)
        if goal is not None:
            fields.append("goal = ?")
            params.append(goal)

        if not fields:
            return True

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?;"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            return cursor.rowcount > 0

    def create_user(
        self,
        name: str,
        arg2: Any = None,
        arg3: Any = None,
        arg4: Any = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        age: int = 25,
        difficulty: str = "Beginner",
        experience: str = "Beginner",
        goal: str = "General Fitness",
    ) -> int:
        """Helper to create or register a user and return their integer ID (supports all calling conventions)."""
        clean_name = str(name).strip()
        user_email = email
        user_pw = password or "password123"
        user_age = age
        user_exp = difficulty or experience or "Beginner"
        user_goal = goal or "General Fitness"

        # Check if 2nd positional argument is age (int) e.g. create_user("John", 30, "Intermediate", "Strength")
        if isinstance(arg2, int):
            user_age = arg2
            if arg3 is not None:
                user_exp = str(arg3)
            if arg4 is not None:
                user_goal = str(arg4)
            if not user_email:
                user_email = f"{clean_name.lower().replace(' ', '_')}@ki.ai"
        elif isinstance(arg2, str) and "@" in arg2:
            user_email = arg2
            if arg3 is not None:
                user_pw = str(arg3)
            if isinstance(arg4, int):
                user_age = arg4
        elif arg2 is not None:
            user_email = str(arg2)

        if not user_email:
            user_email = f"{clean_name.lower().replace(' ', '_')}@ki.ai"

        success, msg, user = self.register_user(
            name=clean_name,
            email=user_email,
            password=user_pw,
            age=user_age,
            experience=user_exp,
            goal=user_goal,
        )
        if success and user:
            return user["id"]
        
        existing = self.get_user_by_email(user_email)
        return existing["id"] if existing else 1

    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Updates user's hashed password securely."""
        pw_hash = hash_password(new_password)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?;", (pw_hash, user_id))
            return cursor.rowcount > 0

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Calculates comprehensive lifetime metrics for a user."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    COUNT(*) AS total_sessions,
                    COALESCE(AVG(average_score), 0.0) AS avg_score,
                    COALESCE(MAX(final_score), 0.0) AS best_score,
                    COALESCE(SUM(duration), 0) AS total_seconds,
                    COALESCE(SUM(hold_duration), 0) AS total_hold_seconds
                FROM practice_sessions
                WHERE user_id = ?;
                """,
                (user_id,),
            )
            row = cursor.fetchone()

            # Find most practiced pose
            cursor.execute(
                """
                SELECT p.name, COUNT(*) as count
                FROM practice_sessions ps
                JOIN poses p ON ps.pose_id = p.id
                WHERE ps.user_id = ?
                GROUP BY ps.pose_id
                ORDER BY count DESC
                LIMIT 1;
                """,
                (user_id,),
            )
            fav_row = cursor.fetchone()
            fav_pose = fav_row["name"] if fav_row else "None yet"

            total_sec = row["total_seconds"] if row else 0
            hold_sec = row["total_hold_seconds"] if row else 0
            avg = round(float(row["avg_score"]), 1) if row else 0.0
            best = round(float(row["best_score"]), 1) if row else 0.0
            sessions_count = row["total_sessions"] if row else 0

            return {
                "total_sessions": sessions_count,
                "completed_sessions": sessions_count,
                "avg_score": avg,
                "overall_avg_score": avg,
                "average_score": avg,
                "best_score": best,
                "total_seconds": total_sec,
                "total_practice_time": total_sec,
                "total_minutes": round(total_sec / 60, 1),
                "total_hold_seconds": hold_sec,
                "total_hold_time": hold_sec,
                "favorite_pose": fav_pose,
                "most_practiced_pose": fav_pose,
            }

    # ==========================================
    # Pose & Rule Seeding & Retrieval
    # ==========================================

    def seed_initial_poses(self) -> None:
        """Seeds predefined yoga poses from data/poses.json if poses table is empty or updates figure_paths."""
        try:
            if not settings.POSES_JSON_PATH.exists():
                logger.warning(f"Poses JSON not found at {settings.POSES_JSON_PATH}")
                return

            with open(settings.POSES_JSON_PATH, "r", encoding="utf-8") as f:
                poses_data = json.load(f)

            with self.get_connection() as conn:
                cursor = conn.cursor()
                for p in poses_data:
                    fig_path = p.get("figure_path") or p.get("pose_figure") or f"assets/pose_figures/{p.get('name', '').lower().replace(' ', '_')}.svg"
                    img_path = p.get("image_path") or f"assets/images/yoga/{p.get('name', '').lower().replace(' ', '_')}.jpg"

                    cursor.execute(
                        """
                        INSERT OR IGNORE INTO poses (
                            id, name, sanskrit_name, category, difficulty, goal,
                            description, benefits, instructions, precautions,
                            image_path, figure_path, hold_duration, is_custom
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0);
                        """,
                        (
                            p.get("id"),
                            p.get("name"),
                            p.get("sanskrit_name"),
                            p.get("category"),
                            p.get("difficulty"),
                            p.get("goal"),
                            p.get("description"),
                            json.dumps(p.get("benefits", [])),
                            json.dumps(p.get("instructions", [])),
                            p.get("precautions"),
                            img_path,
                            fig_path,
                            p.get("hold_duration", 20),
                        ),
                    )
                    # Update existing poses to ensure figure_path and image_path are populated
                    cursor.execute(
                        """
                        UPDATE poses 
                        SET figure_path = ?, image_path = ?
                        WHERE id = ? OR LOWER(name) = LOWER(?);
                        """,
                        (fig_path, img_path, p.get("id"), p.get("name")),
                    )
                    pose_id = p.get("id")

                    # Insert Pose Rules if not present
                    cursor.execute("SELECT COUNT(*) FROM pose_rules WHERE pose_id = ?;", (pose_id,))
                    if cursor.fetchone()[0] == 0:
                        for r in p.get("rules", []):
                            cursor.execute(
                                """
                                INSERT INTO pose_rules (
                                    pose_id, joint_name, target_angle, min_angle, max_angle,
                                    tolerance, weight, feedback_message
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                                """,
                                (
                                    pose_id,
                                    r.get("joint_name"),
                                    r.get("target_angle"),
                                    r.get("target_angle") - r.get("tolerance", 15.0),
                                    r.get("target_angle") + r.get("tolerance", 15.0),
                                    r.get("tolerance", 15.0),
                                    r.get("weight", 15.0),
                                    r.get("feedback_message"),
                                ),
                            )
            logger.info("Initial library poses and figure paths synchronized successfully.")
        except Exception as e:
            logger.error(f"Failed to seed initial poses: {e}")

    def seed_surya_namaskar_poses(self) -> None:
        """Seeds Surya Namaskar 12-step sequence from data/surya_namaskar.json."""
        try:
            if not settings.SURYA_JSON_PATH.exists():
                return

            with open(settings.SURYA_JSON_PATH, "r", encoding="utf-8") as f:
                surya_data = json.load(f)

            with self.get_connection() as conn:
                cursor = conn.cursor()
                for step in surya_data:
                    step_num = step.get("step_number", 1)
                    pose_name = f"Step {step_num}: {step.get('name')}"
                    fig_path = step.get("figure_path") or f"assets/pose_figures/surya_{step_num}.svg"

                    cursor.execute("SELECT id FROM poses WHERE name = ?;", (pose_name,))
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute("UPDATE poses SET figure_path = ? WHERE id = ?;", (fig_path, existing["id"]))
                        continue

                    cursor.execute(
                        """
                        INSERT INTO poses (
                            name, sanskrit_name, category, difficulty, goal,
                            description, benefits, instructions, precautions,
                            image_path, figure_path, hold_duration, is_custom
                        ) VALUES (?, ?, 'Surya Namaskar', ?, ?, ?, ?, ?, ?, ?, ?, ?, 0);
                        """,
                        (
                            pose_name,
                            step.get("sanskrit_name"),
                            step.get("difficulty", "Beginner"),
                            step.get("target_goal", "Flexibility"),
                            step.get("description"),
                            json.dumps([step.get("benefits", "")]),
                            step.get("instructions"),
                            step.get("precautions"),
                            f"assets/images/yoga/surya_{step_num}.png",
                            fig_path,
                            step.get("hold_duration", 10),
                        ),
                    )
                    pose_id = cursor.lastrowid

                    for r in step.get("rules", []):
                        cursor.execute(
                            """
                            INSERT INTO pose_rules (
                                pose_id, joint_name, target_angle, min_angle, max_angle,
                                tolerance, weight, feedback_message
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                            """,
                            (
                                pose_id,
                                r.get("joint_name"),
                                r.get("target_angle"),
                                r.get("target_angle") - r.get("tolerance", 15.0),
                                r.get("target_angle") + r.get("tolerance", 15.0),
                                r.get("tolerance", 15.0),
                                r.get("weight", 20.0),
                                r.get("feedback_message"),
                            ),
                        )
            logger.info("Surya Namaskar poses seeded successfully.")
        except Exception as e:
            logger.error(f"Failed to seed Surya Namaskar poses: {e}")

    def get_all_poses(self) -> List[Dict[str, Any]]:
        """Retrieves all yoga poses with attached rules and figure paths."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT *
                FROM poses
                ORDER BY is_custom ASC, category ASC, id ASC;
                """
            )
            rows = cursor.fetchall()
            poses: List[Dict[str, Any]] = []

            # Pre-fetch all rules
            cursor.execute("SELECT pose_id, joint_name, target_angle, min_angle, max_angle, tolerance, weight, feedback_message FROM pose_rules;")
            all_rules = cursor.fetchall()
            rules_by_pose: Dict[int, List[Dict[str, Any]]] = {}
            for r in all_rules:
                p_id = r["pose_id"]
                if p_id not in rules_by_pose:
                    rules_by_pose[p_id] = []
                rules_by_pose[p_id].append(dict(r))

            for r in rows:
                p_dict = dict(r)
                p_dict["rules"] = rules_by_pose.get(p_dict["id"], [])
                try:
                    p_dict["benefits"] = json.loads(p_dict["benefits"]) if p_dict["benefits"] else []
                except Exception:
                    pass
                try:
                    p_dict["instructions"] = json.loads(p_dict["instructions"]) if p_dict["instructions"] else []
                except Exception:
                    pass

                # Guarantee figure_path exists
                if not p_dict.get("figure_path"):
                    slug = p_dict.get("name", "").lower().replace(" ", "_").replace("step_", "surya_")
                    p_dict["figure_path"] = f"assets/pose_figures/{slug}.svg"

                poses.append(p_dict)
            return poses

    def get_surya_namaskar_poses(self) -> List[Dict[str, Any]]:
        """Retrieves the 12 sequential Surya Namaskar poses."""
        all_poses = self.get_all_poses()
        surya = [p for p in all_poses if p.get("category") == "Surya Namaskar"]
        surya.sort(key=lambda x: x.get("id", 0))
        return surya

    def get_pose_by_id(self, pose_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves a single yoga pose and its rules by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM poses WHERE id = ?;", (pose_id,))
            row = cursor.fetchone()
            if not row:
                return None

            pose_dict = dict(row)
            cursor.execute("SELECT joint_name, target_angle, min_angle, max_angle, tolerance, weight, feedback_message FROM pose_rules WHERE pose_id = ?;", (pose_id,))
            pose_dict["rules"] = [dict(r) for r in cursor.fetchall()]
            try:
                pose_dict["benefits"] = json.loads(pose_dict["benefits"]) if pose_dict["benefits"] else []
            except Exception:
                pass
            try:
                pose_dict["instructions"] = json.loads(pose_dict["instructions"]) if pose_dict["instructions"] else []
            except Exception:
                pass

            if not pose_dict.get("figure_path"):
                slug = pose_dict.get("name", "").lower().replace(" ", "_").replace("step_", "surya_")
                pose_dict["figure_path"] = f"assets/pose_figures/{slug}.svg"

            return pose_dict

    def add_custom_pose(
        self,
        name: str,
        category: str,
        difficulty: str,
        goal: str,
        description: str,
        rules: List[Dict[str, Any]],
        user_id: Optional[int] = None,
        created_by: Optional[int] = None,
        hold_duration: int = 20,
        benefits: Optional[List[str]] = None,
        instructions: Optional[List[str]] = None,
        precautions: str = "",
        image_path: Optional[str] = None,
        reference_data: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Saves a user-created custom yoga pose and its rules."""
        author_id = user_id if user_id is not None else created_by

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO poses (
                    name, sanskrit_name, category, difficulty, goal,
                    description, benefits, instructions, precautions, image_path,
                    hold_duration, is_custom, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?);
                """,
                (
                    name.strip(),
                    name.strip(),
                    category,
                    difficulty,
                    goal,
                    description,
                    json.dumps(benefits or []),
                    json.dumps(instructions or []),
                    precautions,
                    image_path,
                    hold_duration,
                    author_id,
                ),
            )
            pose_id = cursor.lastrowid

            for r in rules:
                cursor.execute(
                    """
                    INSERT INTO pose_rules (
                        pose_id, joint_name, target_angle, min_angle, max_angle,
                        tolerance, weight, feedback_message
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        pose_id,
                        r.get("joint_name"),
                        r.get("target_angle"),
                        r.get("min_angle", r.get("target_angle") - r.get("tolerance", 15.0)),
                        r.get("max_angle", r.get("target_angle") + r.get("tolerance", 15.0)),
                        r.get("tolerance", settings.DEFAULT_TOLERANCE_DEGREES),
                        r.get("weight", 15.0),
                        r.get("feedback_message", f"Adjust your {r.get('joint_name', '').replace('_', ' ')}"),
                    ),
                )

            if reference_data:
                cursor.execute(
                    """
                    INSERT INTO custom_pose_templates (pose_id, reference_data)
                    VALUES (?, ?);
                    """,
                    (pose_id, json.dumps(reference_data)),
                )

            logger.info(f"Custom pose '{name}' created successfully with ID: {pose_id}")
            return pose_id

    def get_custom_template(self, pose_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves stored custom template reference data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT reference_data FROM custom_pose_templates WHERE pose_id = ?;", (pose_id,))
            row = cursor.fetchone()
            if row and row["reference_data"]:
                try:
                    return json.loads(row["reference_data"])
                except Exception:
                    return {}
            return None

    def get_user_sessions(self, user_id: int, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieves sessions recorded for a user with optional limit."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = """
                SELECT ps.id, ps.pose_id, p.name AS pose_name, p.category, p.difficulty,
                       ps.duration, ps.average_score, ps.final_score, ps.hold_duration,
                       ps.corrections_count, ps.created_at
                FROM practice_sessions ps
                JOIN poses p ON ps.pose_id = p.id
                WHERE ps.user_id = ?
                ORDER BY ps.created_at DESC
            """
            params = [user_id]
            if limit is not None and limit > 0:
                query += " LIMIT ?"
                params.append(limit)
            query += ";"
            cursor.execute(query, tuple(params))
            return [dict(r) for r in cursor.fetchall()]

    # ==========================================
    # Practice Session & History CRUD
    # ==========================================

    def save_practice_session(
        self,
        user_id: int,
        pose_id: int,
        duration: int,
        average_score: float,
        final_score: float,
        hold_duration: int = 0,
        corrections_count: int = 0,
        feedback_items: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        """Records completed practice session and optional feedback logs."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO practice_sessions (
                    user_id, pose_id, duration, average_score, final_score,
                    hold_duration, corrections_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?);
                """,
                (user_id, pose_id, duration, average_score, final_score, hold_duration, corrections_count),
            )
            session_id = cursor.lastrowid

            if feedback_items:
                for fb in feedback_items:
                    cursor.execute(
                        """
                        INSERT INTO feedback (session_id, body_part, message, accuracy)
                        VALUES (?, ?, ?, ?);
                        """,
                        (session_id, fb.get("body_part", "general"), fb.get("message", ""), float(fb.get("accuracy", average_score))),
                    )

            logger.info(f"Practice session recorded. ID: {session_id}, Avg Score: {average_score:.1f}%")
            return session_id

    def get_recent_sessions(self, user_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieves recent workout history with pose names."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ps.id, ps.pose_id, p.name AS pose_name, p.category, p.difficulty,
                       ps.duration, ps.average_score, ps.final_score, ps.hold_duration,
                       ps.corrections_count, ps.created_at
                FROM practice_sessions ps
                JOIN poses p ON ps.pose_id = p.id
                WHERE ps.user_id = ?
                ORDER BY ps.created_at DESC
                LIMIT ?;
                """,
                (user_id, limit),
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_all_practice_history(
        self,
        user_id: int,
        pose_filter: Optional[str] = None,
        min_score: Optional[float] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Retrieves filterable practice history."""
        query = """
            SELECT ps.id, ps.pose_id, p.name AS pose_name, p.category, p.difficulty,
                   ps.duration, ps.average_score, ps.final_score, ps.hold_duration,
                   ps.corrections_count, ps.created_at
            FROM practice_sessions ps
            JOIN poses p ON ps.pose_id = p.id
            WHERE ps.user_id = ?
        """
        params: List[Any] = [user_id]

        if pose_filter and pose_filter != "All":
            query += " AND p.name LIKE ?"
            params.append(f"%{pose_filter}%")
        if min_score is not None and min_score > 0:
            query += " AND ps.average_score >= ?"
            params.append(min_score)

        query += " ORDER BY ps.created_at DESC LIMIT ?;"
        params.append(limit)

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            return [dict(r) for r in cursor.fetchall()]

    def get_analytics_score_progression(self, user_id: int) -> List[Dict[str, Any]]:
        """Retrieves chronological score samples for progress charts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ps.id, ps.average_score, ps.final_score, ps.created_at, p.name AS pose_name
                FROM practice_sessions ps
                JOIN poses p ON ps.pose_id = p.id
                WHERE ps.user_id = ?
                ORDER BY ps.created_at ASC;
                """,
                (user_id,),
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_score_history_timeline(self, user_id: int, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieves chronological score timeline for progress window charts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT ps.id, ps.average_score, ps.final_score, ps.created_at, p.name AS pose_name
                FROM practice_sessions ps
                JOIN poses p ON ps.pose_id = p.id
                WHERE ps.user_id = ?
                ORDER BY ps.created_at ASC
                LIMIT ?;
                """,
                (user_id, limit),
            )
            return [dict(r) for r in cursor.fetchall()]

    def get_pose_performance_breakdown(self, user_id: int) -> List[Dict[str, Any]]:
        """Returns average accuracy grouped by pose for comparative bar charts."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT p.name AS pose_name, 
                       AVG(ps.average_score) AS avg_score,
                       COUNT(ps.id) AS session_count,
                       MAX(ps.average_score) AS best_score
                FROM practice_sessions ps
                JOIN poses p ON ps.pose_id = p.id
                WHERE ps.user_id = ?
                GROUP BY ps.pose_id
                ORDER BY avg_score DESC;
                """,
                (user_id,),
            )
            return [dict(r) for r in cursor.fetchall()]
