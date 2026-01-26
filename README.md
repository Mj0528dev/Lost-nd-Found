Lost & Found System (Backend Core)

Overview
This project is a backend core system for a Lost & Found application.
It implements the data models, validation logic, claim scoring engine, audit logging, and admin verification workflow without an HTTP/API layer yet.
The goal of this phase is correctness, structure, and testability of the backend logic before exposing it via an API.
________________________________________
Project Status
Current Phase: v0.2.0 — Phase 1 Complete
✅ Database schema
✅ Model-layer business logic
✅ Claim validation rules
✅ Claim scoring engine
✅ Admin claim verification
✅ Audit logging
✅ One-run integration test (no pytest)
🚫 No HTTP / Flask API yet (planned for Phase 2)
________________________________________
Core Features Implemented
Items
•	Create and retrieve found items
•	SQLite-backed persistence
Claims
•	Submit claims for found items
•	Automatic rule-based claim scoring
•	Claim status lifecycle (pending → approved / rejected)
Validation
•	Required-field enforcement
•	Claim anomaly checks (e.g. no receipt, high amount, missing description)
•	Centralized validation helpers
Admin Actions
•	Approve or reject claims
•	Prevent double-processing of claims
Audit Logging
•	Every critical action is recorded in audit_logs
•	Tracks:
o	action
o	entity type
o	entity ID
o	actor
o	timestamp
Testing
•	Single-run integration test
•	No pytest required
•	Verifies:
o	database initialization
o	table creation
o	found item creation & retrieval
o	claim validation (positive & negative)
o	claim scoring
o	claim creation
o	admin verification
o	audit logging
________________________________________
Tech Stack
•	Python 3
•	SQLite
•	Standard library only (no ORM)
•	No web framework in this phase
________________________________________
Project Structure
backend/
│
├── app.py                  # Entry point (DB init hook)
├── test.py                 # One-run integration test
│
├── models/
│   ├── __init__.py
│   ├── base.py              # DB connection & schema
│   ├── items.py             # Found item logic
│   ├── claims.py            # Claim lifecycle
│   ├── audit.py             # Audit logging
│   └── validators.py        # Core validators
│
├── helpers/
│   ├── __init__.py
│   └── claim_validation.py  # Claim anomaly rules
│
├── services/
│   └── claim_scoring.py     # Rule-based scoring engine
│
└── database.db              # SQLite database (generated)
________________________________________
Setup Instructions
1️ Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate
2️ Install dependencies
pip install -r requirements.txt
(If empty, this is expected for Phase 1)
________________________________________
3️ Initialize the database
python app.py
This will:
•	create database.db
•	initialize all required tables
________________________________________
4️ Run the full integration test
Open a separate terminal and run:
python test.py
Expected final output:
✅ ALL TESTS PASSED SUCCESSFULLY
If a test fails, the script exits immediately with a clear error message indicating what broke and where.
________________________________________
How Testing Works (Important)
•	This project intentionally does not use pytest
•	The test script:
o	runs against the real database
o	truncates tables before testing
o	validates real inserts, reads, updates, and logs
•	Designed for clarity and debuggability, not test frameworks
________________________________________
Versioning & Git Workflow
•	Stable releases are tagged (e.g. v0.2.0)
•	Phase work is done on feature branches
•	main remains clean and stable
________________________________________
Roadmap
Phase 2 (Planned)
•	Flask API layer
•	HTTP routes mapping to existing logic
•	Proper status codes & JSON responses
Phase 3 (Optional)
•	Authentication
•	Role-based access
•	Frontend or admin dashboard
________________________________________
Notes
This repository represents a clean, testable backend foundation designed to be extended — not rewritten — when an API layer is added.

