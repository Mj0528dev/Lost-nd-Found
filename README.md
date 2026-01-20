# Lost & Found System

## Overview

A simple backend system for reporting lost and found items, submitting ownership claims, and allowing admins to verify claims. The API follows proper HTTP semantics and supports clean database resets for repeatable testing.

## Features

* Report lost items
* Report found items
* Submit claims for found items
* Automatic claim scoring
* Admin review and verification of claims
* Safe database reset and reinitialization

## Tech Stack

* Python
* Flask
* SQLite

## Setup Instructions

1. Create and activate a virtual environment
2. Install dependencies
3. Initialize the database
4. Run the Flask app

```bash
pip install -r requirements.txt
python -c "from models import init_db; init_db()"
python app.py
```

The API will be available at:

```
http://127.0.0.1:5000
```

## 🧪 API Testing Guide (Windows CMD – Single Line Commands)

> All commands below are written as **single-line curl commands** compatible with Windows Command Prompt.

### 1️⃣ Report a Lost Item

```bash
curl -X POST http://127.0.0.1:5000/lost -H "Content-Type: application/json" -d "{\"category\":\"Electronics\",\"last_seen_location\":\"Library\",\"lost_datetime\":\"2026-01-20T10:00:00\",\"public_description\":\"Black wireless earbuds\",\"private_details\":\"Scratch on left earbud\"}"
```

Expected response:

```json
{"message":"Lost item reported successfully"}
```

---

### 2️⃣ Report a Found Item

```bash
curl -X POST http://127.0.0.1:5000/found -H "Content-Type: application/json" -d "{\"category\":\"Electronics\",\"found_location\":\"Library\",\"found_datetime\":\"2026-01-20T11:00:00\",\"public_description\":\"Found black earbuds near table\"}"
```

Expected response:

```json
{"message":"Found item reported successfully"}
```

---

### 3️⃣ Submit a Claim for the Found Item

```bash
curl -X POST http://127.0.0.1:5000/claim -H "Content-Type: application/json" -d "{\"found_item_id\":1,\"category\":\"Electronics\",\"last_seen_location\":\"Library\",\"lost_datetime\":\"2026-01-20T10:00:00\",\"private_details\":\"Scratch on left earbud\"}"
```

Expected response:

```json
{"message":"Claim submitted successfully","score":0}
```

---

### 4️⃣ Admin: View Pending Claims

```bash
curl http://127.0.0.1:5000/admin/claims
```

Expected response: list of pending claims with score and status.

---

### 5️⃣ Admin: Verify (Approve) a Claim

```bash
curl -X POST http://127.0.0.1:5000/admin/claims/1/verify -H "Content-Type: application/json" -d "{\"decision\":\"approved\",\"admin_username\":\"admin1\"}"
```

Expected response:

```json
{"message":"Claim approved successfully"}
```

---

### 6️⃣ Confirm Claim Is No Longer Pending

```bash
curl http://127.0.0.1:5000/admin/claims
```

Expected response:

```json
[]
```

---

### 7️⃣ Attempt to Re-verify a Processed Claim (Expected Error)

```bash
curl -X POST http://127.0.0.1:5000/admin/claims/1/verify -H "Content-Type: application/json" -d "{\"decision\":\"rejected\",\"admin_username\":\"admin2\"}"
```

Expected response:

```json
{"error":"Claim already processed"}
```

---

### 8️⃣ View Found Items

```bash
curl http://127.0.0.1:5000/found
```

Expected response: list of found items stored in the system.

---

### ⚠ Expected HTTP Errors

* `GET /found` without POST → **405 Method Not Allowed** (correct behavior)
* Invalid routes → **404 Not Found**
* Missing required fields → **400 Bad Request**

## Future Improvements

* User authentication
* Role-based admin access
* Partial-match claim scoring UI
* Admin dashboard (frontend)
* Image uploads for items
