# Lost & Found System — Backend Core

> A production-ready backend foundation for a Lost & Found platform, focused on **data integrity, validation, scoring logic, auditability, and testability**.

---

## 📌 Overview

This project implements the **core backend logic** of a Lost & Found system **before** introducing an HTTP/API layer.

Instead of starting with routes and UI, this system prioritizes:

- Clean data modeling
- Explicit validation
- Deterministic business logic
- Auditable admin actions
- Repeatable integration testing

This mirrors **real-world backend backend engineering practices**, where correctness and maintainability come first.

---

## 🎯 Why This Project Matters

Many beginner projects jump straight to APIs and UIs.  
This project intentionally **does not** — and that’s the point.

It demonstrates:

- Separation of concerns
- Defensive programming
- Clear domain modeling
- Testable business logic
- Readiness for future API layers

Everything here can be exposed via REST **without refactoring**.

---

## 🧭 Project Status

**Current Version:** `v0.2.0`  
**Phase:** Backend Core (Phase 1.3) — Complete

---

## ✨ Core Features

### 📦 Found Items

- Create and persist found items
- Retrieve items by ID
- Normalized SQLite storage

### 📝 Claims

- Submit ownership claims for found items
- Claims start in a `pending` state
- Prevents invalid or duplicate processing

### 🧮 Claim Scoring Engine

- Rule-based weighted scoring
- Supports exact and partial matches
- Returns:
  - Total score
  - Matched fields
  - Detailed breakdown

This enables **explainable decisions** and **admin transparency**.

### ✅ Claim Validation

Centralized validation rules detect anomalies such as:

- Missing receipts
- Unusually high claim amounts
- Missing descriptions

Validation is **decoupled from persistence** and reusable.

### 🛡 Admin Verification

- Admins can approve or reject claims
- Claims cannot be processed twice
- Status transitions enforced at the model layer

### 🧾 Audit Logging

All critical actions are logged:

- Claim creation
- Admin decisions
- System actions

Each log stores:

- Action
- Entity type
- Entity ID
- Actor
- Timestamp

---

## 🧪 Testing Strategy

This project uses a **single-run integration test** (`test.py`) instead of pytest.

### Why this approach?

- No hidden fixtures
- No test magic
- Explicit execution order
- Easy debugging

### What is tested

- Database initialization
- Table creation
- Found item creation & retrieval
- Claim validation (positive & negative)
- Claim scoring correctness
- Claim creation
- Admin verification
- Audit log persistence

The test exits immediately on failure with a **clear error message**.

---

## 🛠 Tech Stack

- Python 3
- SQLite
- Python Standard Library
- No ORM
- No web framework (yet)

---

## 📁 Project Structure

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
