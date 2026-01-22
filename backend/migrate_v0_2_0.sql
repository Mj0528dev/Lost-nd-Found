-- ===============================
-- Migration: v0.1.0 → v0.2.0
-- Safe, additive-only migration
-- ===============================

BEGIN TRANSACTION;

-- USERS TABLE (auth foundation)
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT CHECK(role IN ('user', 'admin')) NOT NULL,
    email TEXT,
    is_verified INTEGER DEFAULT 0,
    created_at TEXT NOT NULL
);

-- ADMIN ACTION LOGS (audit trail)
CREATE TABLE IF NOT EXISTS admin_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_username TEXT NOT NULL,
    claim_id INTEGER NOT NULL,
    action TEXT CHECK(action IN ('approved', 'rejected')) NOT NULL,
    reason TEXT,
    created_at TEXT NOT NULL
);

COMMIT;
