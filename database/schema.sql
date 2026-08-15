-- =========================================================
-- KI.AI — AI-Powered Yoga & Posture Intelligence
-- Database Relational Schema (SQLite)
-- =========================================================

PRAGMA foreign_keys = ON;

-- Users Table with Auth & Profile support
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    age INTEGER DEFAULT 25,
    experience TEXT NOT NULL DEFAULT 'Beginner',
    goal TEXT NOT NULL DEFAULT 'General Fitness',
    avatar_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Yoga Poses Table
CREATE TABLE IF NOT EXISTS poses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    sanskrit_name TEXT,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    goal TEXT NOT NULL,
    description TEXT,
    benefits TEXT,
    instructions TEXT,
    precautions TEXT,
    image_path TEXT,
    figure_path TEXT,
    hold_duration INTEGER DEFAULT 20,
    is_custom INTEGER DEFAULT 0,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Pose Rules Table
CREATE TABLE IF NOT EXISTS pose_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pose_id INTEGER NOT NULL,
    joint_name TEXT NOT NULL,
    target_angle REAL NOT NULL,
    min_angle REAL NOT NULL,
    max_angle REAL NOT NULL,
    tolerance REAL NOT NULL DEFAULT 15.0,
    weight REAL NOT NULL DEFAULT 15.0,
    feedback_message TEXT,
    FOREIGN KEY (pose_id) REFERENCES poses(id) ON DELETE CASCADE
);

-- Practice Sessions Table
CREATE TABLE IF NOT EXISTS practice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pose_id INTEGER NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER NOT NULL DEFAULT 0,
    average_score REAL NOT NULL DEFAULT 0.0,
    final_score REAL NOT NULL DEFAULT 0.0,
    hold_duration INTEGER NOT NULL DEFAULT 0,
    corrections_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pose_id) REFERENCES poses(id) ON DELETE CASCADE
);

-- Detailed Feedback Log Table
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    body_part TEXT NOT NULL,
    message TEXT NOT NULL,
    accuracy REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES practice_sessions(id) ON DELETE CASCADE
);

-- Custom Pose Templates Table
CREATE TABLE IF NOT EXISTS custom_pose_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pose_id INTEGER NOT NULL UNIQUE,
    reference_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pose_id) REFERENCES poses(id) ON DELETE CASCADE
);

-- Indexes for lightning fast queries
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_poses_category ON poses(category);
CREATE INDEX IF NOT EXISTS idx_poses_difficulty ON poses(difficulty);
CREATE INDEX IF NOT EXISTS idx_poses_goal ON poses(goal);
CREATE INDEX IF NOT EXISTS idx_pose_rules_pose_id ON pose_rules(pose_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON practice_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_pose ON practice_sessions(pose_id);
CREATE INDEX IF NOT EXISTS idx_sessions_created ON practice_sessions(created_at);
