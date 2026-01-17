CREATE TABLE IF NOT EXISTS lost_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    item_type TEXT NOT NULL,
    color TEXT,
    brand TEXT,
    last_seen_location TEXT NOT NULL,
    last_seen_datetime TEXT NOT NULL,
    public_description TEXT,
    private_details TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'published',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS found_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    item_type TEXT NOT NULL,
    color TEXT,
    brand TEXT,
    found_location TEXT NOT NULL,
    found_datetime TEXT NOT NULL,
    public_description TEXT,
    status TEXT NOT NULL DEFAULT 'published',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    found_item_id INTEGER NOT NULL,
    claimant_name TEXT NOT NULL,
    claimant_email TEXT NOT NULL,
    answers TEXT NOT NULL,
    verification_score INTEGER NOT NULL,
    decision TEXT NOT NULL DEFAULT 'pending',
    decision_reason TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (found_item_id) REFERENCES found_items(id)
);

CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    performed_by TEXT NOT NULL,
    timestamp TEXT NOT NULL
);
