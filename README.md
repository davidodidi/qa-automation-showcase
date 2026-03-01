# 🧪 QA Automation Showcase Framework

[![CI Pipeline](https://github.com/davidodidi/qa-automation-showcase/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/qa-automation-showcase/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/playwright-latest-green.svg)](https://playwright.dev/)
[![Robot Framework](https://img.shields.io/badge/Robot_Framework-7.x-red.svg)](https://robotframework.org/)
[![Allure Report](https://img.shields.io/badge/report-Allure-brightgreen.svg)](https://YOUR_USERNAME.github.io/qa-automation-showcase/allure-report)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A production-grade, full-stack test automation framework covering **UI testing**, **REST API testing**, **database validation**, and **CI/CD** — built with Python, Playwright, pytest, and Robot Framework.

📊 **[Live Allure Report →](https://davidodidi.github.io/qa-automation-showcase/allure-report)**

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    QA Automation Framework                      │
├───────────────┬──────────────┬───────────────┬─────────────────┤
│   UI Layer    │  API Layer   │   DB Layer    │  Robot Layer    │
│               │              │               │                 │
│  Playwright   │    httpx     │  SQLAlchemy   │ Robot Framework │
│  pytest-pw    │   requests   │   SQLite      │ RequestsLibrary │
│  Page Objects │  Pydantic    │  Shadow DB    │ Custom Keywords │
│  Screenshots  │  Schema Val  │  Data Integ.  │ Keyword-driven  │
└───────┬───────┴──────┬───────┴───────┬───────┴────────┬────────┘
        │              │               │                │
        └──────────────┴───────────────┴────────────────┘
                                │
                    ┌───────────▼──────────┐
                    │   GitHub Actions CI  │
                    │                      │
                    │  lint → api → db     │
                    │       ↓              │
                    │  ui (chromium+ff)    │
                    │       ↓              │
                    │  robot framework     │
                    │       ↓              │
                    │  allure → gh-pages   │
                    └──────────────────────┘
```

---

## ✨ Key Features

| Feature | Implementation |
|---|---|
| **UI Testing** | Playwright + Page Object Model, auto-screenshot on failure |
| **API Testing** | httpx client, Pydantic schema validation, CRUD lifecycle |
| **Database Validation** | SQLAlchemy shadow DB, data integrity assertions after every API call |
| **Robot Framework** | Keyword-driven smoke + regression suites, readable by non-engineers |
| **CI/CD Pipeline** | GitHub Actions: lint → API → DB → UI (browser matrix) → Robot → Allure |
| **Parallel Execution** | pytest-xdist: `make test-parallel` runs with `-n auto` workers |
| **Test Data** | Faker-powered `DataFactory` — unique data on every run |
| **Auto-Retry** | pytest-rerunfailures + tenacity for flaky API resilience |
| **Allure Reporting** | Auto-published to GitHub Pages on every merge to `main` |
| **Multi-environment** | Pydantic `BaseSettings` + `environments.yaml` — switch via `ENV=staging` |

---

## 🎯 The "Holy Trinity" Test Pattern

The database validation tests demonstrate the **full data lifecycle** — a pattern used in enterprise QA:

```
Step 1: Create booking via REST API    →  Assert 200 + schema
Step 2: Write response to shadow DB    →  SQLAlchemy ORM
Step 3: Query shadow DB                →  Assert data matches exactly
Step 4: PATCH booking via API          →  Assert 200
Step 5: Update shadow DB record        →  Sync state
Step 6: Delete via API                 →  Assert 201
Step 7: Assert DB record removed       →  Integrity confirmed ✅
```

---

## 📁 Project Structure

```
qa-automation-showcase/
├── .github/
│   └── workflows/
│       ├── ci.yml               # Main CI: lint → api → db → ui → robot → report
│       └── nightly.yml          # Full regression at 2am UTC
├── tests/
│   ├── api/
│   │   ├── clients/
│   │   │   └── booking_client.py    # httpx API client with retry logic
│   │   ├── conftest.py              # Session-scoped fixtures + auth
│   │   ├── test_auth_api.py         # Auth endpoint tests
│   │   └── test_booking_crud.py     # Full CRUD test suite
│   ├── database/
│   │   ├── db_client.py             # SQLAlchemy shadow DB client
│   │   ├── conftest.py
│   │   └── test_db_integrity.py     # Data integrity validation
│   ├── ui/
│   │   ├── pages/
│   │   │   ├── base_page.py         # Base POM with shared helpers
│   │   │   └── home_page.py         # Home + Admin login page objects
│   │   ├── conftest.py              # Playwright fixtures + auto-screenshot
│   │   ├── test_home_page.py        # Home page UI tests
│   │   └── test_admin_login.py      # Admin panel auth tests
│   └── robot/
│       ├── resources/
│       │   ├── keywords.robot       # Reusable keyword library
│       │   └── variables.robot      # Test configuration
│       ├── api_smoke.robot          # API smoke suite
│       └── booking_smoke.robot      # Booking regression suite
├── config/
│   ├── settings.py              # Pydantic BaseSettings (env-aware)
│   └── environments.yaml        # Per-environment config
├── utils/
│   ├── data_factory.py          # Faker-based test data generation
│   └── assertions.py            # Custom domain assertions + Pydantic schemas
├── Makefile                     # Developer commands
├── pyproject.toml
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Git

### 1. Clone & Install

```bash
git clone https://github.com/davidodidi/qa-automation-showcase.git
cd qa-automation-showcase

# Create virtual environment
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# Install all dependencies + browsers
make setup
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env if needed (defaults work out of the box)
```

### 3. Run Tests

```bash
# Fast smoke tests (< 3 minutes)
make test-smoke

# Individual layers
make test-api          # REST API tests
make test-db           # Database validation
make test-ui           # UI tests (headless)
make test-ui-headed    # UI tests (watch mode — great for demos!)
make test-robot        # Robot Framework suites

# Everything
make test-all

# Generate + open Allure report
make report
```

---

## 🔧 Technology Stack

| Layer | Technology | Why |
|---|---|---|
| **Test Runner** | pytest 8.x | Industry standard, rich plugin ecosystem |
| **UI Automation** | Playwright | Modern, fast, reliable, supports all browsers |
| **API Client** | httpx | async-ready, better type hints than requests |
| **DB ORM** | SQLAlchemy 2.x | Industry-standard, type-safe mapped columns |
| **Schema Validation** | Pydantic v2 | Fast, Pythonic, excellent error messages |
| **BDD/Keyword** | Robot Framework 7 | Readable by PMs and non-engineers |
| **Test Data** | Faker | Unique, realistic data — no hardcoding |
| **Retry Logic** | tenacity | Resilient against flaky third-party APIs |
| **Reporting** | Allure 2 | Beautiful, interactive, CI-integrated |
| **CI/CD** | GitHub Actions | Industry standard, free for public repos |
| **Parallelism** | pytest-xdist | `-n auto` uses all available CPU cores |
| **Config** | Pydantic BaseSettings | Type-safe, env-var override, multi-env |

---

## 🧪 Test Suite Overview

### API Tests (`tests/api/`)
- ✅ Auth happy path and negative paths
- ✅ GET all bookings — schema and list validation
- ✅ GET single booking — data integrity
- ✅ POST create booking — schema + data match
- ✅ PUT full update — field replacement
- ✅ PATCH partial update — selective field change
- ✅ DELETE — 201 response + subsequent 404
- ✅ Response time assertions (SLA-aware)
- ✅ Unauthorised request returns 403

### Database Tests (`tests/database/`)
- ✅ Created booking persisted to shadow DB correctly
- ✅ Deleted booking removed from DB
- ✅ Bulk insert — count accuracy
- ✅ Date format validation (YYYY-MM-DD)
- ✅ PATCH reflected in shadow DB after sync

### UI Tests (`tests/ui/`)
- ✅ Home page load and hero element visibility
- ✅ Room listings displayed (count ≥ 1)
- ✅ Contact form — valid submission success
- ✅ Admin login page loads with all elements
- ✅ Valid credentials → rooms dashboard
- ✅ Login/logout cycle
- ✅ Invalid credentials rejected (stays on login page)
- ✅ Auto-screenshot on test failure

### Robot Framework (`tests/robot/`)
- ✅ Health check — API reachable
- ✅ Auth token generation
- ✅ Create/Read/Update/Delete lifecycle
- ✅ Negative: 404 on non-existent booking
- ✅ Negative: 403 on unauthenticated update
- ✅ Data integrity: depositpaid is boolean
- ✅ Performance: response under 5s

---

## 🔄 CI/CD Pipeline

```
Push to main/PR
      │
      ▼
  ┌─────────┐
  │  Lint   │  ruff static analysis
  └────┬────┘
       │
  ┌────▼────┐    ┌──────────────┐
  │   API   │    │   UI Tests   │  (chromium + firefox in parallel)
  │  Tests  │    └──────┬───────┘
  └────┬────┘           │
       │           ┌────▼─────┐
  ┌────▼────┐      │  Robot   │
  │   DB    │      │Framework │
  │ Validate│      └────┬─────┘
  └────┬────┘           │
       └────────┬────────┘
                │
          ┌─────▼──────┐
          │   Allure   │  → GitHub Pages (live report)
          │   Report   │
          └────────────┘
```

The pipeline runs on every push and PR. The Allure report is automatically published to GitHub Pages after every merge to `main`.

---

## 📊 Reports

After running locally:

```bash
make report        # Allure (interactive, with step details)
make report-robot  # Robot Framework HTML report
```

Or view the live CI report: **[📊 Allure Report](https://davidodidi.github.io/qa-automation-showcase/allure-report)**

---

## 🎨 Design Decisions

**Why httpx over requests?**
httpx is async-ready and has better type hints. The `BookingClient` is designed to be easily upgraded to async with minimal changes.

**Why a shadow database?**
In real projects, QA engineers often validate that API operations produce the correct database state. The SQLite shadow DB simulates this pattern without needing access to the application's actual database.

**Why both pytest and Robot Framework?**
They serve different audiences. pytest is for technical test engineers who want full Python flexibility. Robot Framework produces keyword-driven reports that PMs, BAs, and stakeholders can read without knowing Python.

**Why Pydantic for schema validation?**
Pydantic v2 gives us automatic type coercion, clear validation errors, and schema documentation in one package. Much cleaner than manual dict assertions.

---

## 📜 License

MIT — feel free to use this as a template for your own projects.
