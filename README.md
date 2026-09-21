# FoodRescue — Surplus Food Redistribution Platform

> A production-ready, full-stack platform connecting surplus food providers (restaurants, college canteens, bakeries, caterers) with verified recipients (NGOs, shelters, community kitchens) before food becomes waste.

---

## 📌 Table of Contents

1. [Project Overview](#-project-overview)
2. [Problem Statement & Solution](#-problem-statement--solution)
3. [Key Implemented Features](#-key-implemented-features)
4. [Technology Stack](#-technology-stack)
5. [Architecture & Concurrency Design](#-architecture--concurrency-design)
6. [Application Walkthrough & User Flows](#-application-walkthrough--user-flows)
7. [Pre-Seeded Demo Accounts](#-pre-seeded-demo-accounts)
8. [Getting Started & How to Run](#-getting-started--how-to-run)
9. [Running Celery & Redis Background Jobs](#-running-celery--redis-background-jobs)
10. [Automated Testing Suite](#-automated-testing-suite)
11. [REST API Documentation](#-rest-api-documentation)
12. [Repository Structure](#-repository-structure)

---

## 🌍 Project Overview

**FoodRescue** bridges the gap between commercial surplus food and local communities experiencing food insecurity. Rather than allowing edible, freshly prepared meals to expire and end up in landfills, food providers can publish surplus batches in seconds, and nearby verified NGOs can reserve and collect them before expiration.

### Core Participants:
- **Food Providers**: Restaurants, corporate/college canteens, bakeries, banquet caterers, hostels, grocery outlets.
- **Recipients**: Registered NGOs, homeless shelters, orphanages, community soup kitchens, relief volunteers.
- **Administrators**: Platform operators verifying entities and monitoring surplus redistribution health.

---

## 💡 Problem Statement & Solution

```text
Traditional Food Waste Cycle:
Surplus Food ➔ No Immediate Recipient ➔ Shelf Expiry ➔ Landfill Waste (Methane Emissions)

FoodRescue Life Cycle:
Surplus Food ➔ Listed on Platform ➔ Dietary Verification ➔ Concurrency-Safe Reservation ➔ Pickup OTP Handover ➔ Food Rescued & Tracked
```

---

## 🌟 Key Implemented Features

### 1. Robust SQLite Database with WAL Mode
- **Zero-error local & containerized deployment**: Configured with `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`, `PRAGMA foreign_keys=ON`, and `PRAGMA busy_timeout=15000`.
- Eliminates database locking issues during concurrent reads and writes.
- Works seamlessly in both local environments and persistent Docker volumes (`sqlite_data`). Ready for PostgreSQL via standard `DATABASE_URL`.

### 2. Prominent Dietary Classification & Allergen Safety
- **High-visibility dietary classification** ensures NGOs and shelters know exactly what food it is before booking:
  - 🟢 **100% Vegetarian**
  - 🔴 **Non-Vegetarian**
  - 🌱 **Pure Vegan**
  - 🍞 **Bakery & Bread**
  - 🍱 **Standard Cooked Meals**
- **Allergen disclosures** prominently highlighted on cards and details.
- **Mandatory dietary verification checkbox** inside the reservation modal ensuring safe community distribution.
- One-click dietary filter pills on the browse page.

### 3. Concurrency-Safe Reservation Workflow
- Prevents double-booking and stock race conditions:
  - Database row-level locking ensures atomic stock decrement.
  - Returns `409 Conflict` if requested portions exceed remaining stock.
  - Automatic status transitions (`AVAILABLE` ➔ `PARTIALLY_RESERVED` ➔ `FULLY_RESERVED`).
  - Atomic inventory restoration if a reservation is cancelled by the recipient or declined by the provider.

### 4. Background Expiration & Scheduling Engine
- **Celery + Celery Beat + Redis**:
  - `check_expired_listings_task`: Runs every 60 seconds to detect past-due listings, mark them `EXPIRED`, cancel pending unfulfilled reservations, and notify affected users.
  - `generate_daily_impact_task`: Runs nightly to calculate aggregate rescued meals and carbon offsets.
- **Resilient In-Process Scheduler**: Powered by `APScheduler`, automatically runs in the background during local Windows development without requiring external Redis or Docker processes.

### 5. Rule-Based Recipient Matching System
- Automatically matches newly published surplus food against active recipient preferences (by city, dietary filter, and food category).
- Sends instant notifications to nearby NGOs: *"A food donation matching your preferences is available nearby!"*.

### 6. Interactive Environmental Impact Dashboard
- Live tracking of:
  - **Total Meals Rescued**
  - **Carbon Emissions Prevented**: Computed at **2.5 kg CO₂e saved per meal portion** (EPA / FAO food waste benchmark).
  - **Active Providers & Participating NGOs**.
- **Chart.js Monthly Rescues Bar Chart** and **Category Distribution Doughnut Chart**.

### 7. Digital Collection Passes & Pickup Verification Terminal
- Generates unique, tamper-proof pickup codes (e.g. `FR-10492`).
- Providers use an in-app verification terminal to confirm recipient codes on handover and record verified pickups.

---

## 🛠 Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | **Vue.js 3** (Composition API, `<script setup>`) | High-performance reactive UI |
| **Build Tool** | **Vite** | Sub-second HMR and optimized production bundling |
| **State Management** | **Pinia** | Centralized reactive stores for auth, food, and notifications |
| **Routing** | **Vue Router 4** | Role-based navigation guards and route protection |
| **Styling** | **Tailwind CSS** | Responsive, accessible UI design with custom brand palette |
| **Charting** | **Chart.js** & **vue-chartjs** | Interactive impact charts and distributions |
| **HTTP Client** | **Axios** | JWT interceptors and error handling |
| **Backend Framework**| **Flask 3.0** | RESTful API architecture and blueprint routing |
| **ORM** | **SQLAlchemy** & **Flask-SQLAlchemy** | Concurrency-safe transactions and relationships |
| **Database** | **SQLite (WAL Mode)** / **PostgreSQL** | Concurrent persistence with zero lock contention |
| **Authentication** | **PyJWT** & **Werkzeug** | Secure password hashing and token-based RBAC |
| **Task Queue** | **Celery 5.4** | Asynchronous background processing |
| **Scheduled Tasks** | **Celery Beat** & **APScheduler** | Expiration checker and nightly aggregation |
| **Message Broker** | **Redis 7** | Broker for Celery tasks |
| **Testing** | **pytest** | Automated test suite for concurrency and workflows |
| **Containerization** | **Docker** & **Docker Compose** | Production orchestration of backend, frontend, redis, and workers |

---

## 🏗 Architecture & Concurrency Design

```text
┌──────────────────────────────────────────────────────────┐
│              Vue 3 SPA (Vite + Tailwind)                │
│   (Browse, Dietary Filter, Dashboards, Digital Pass)     │
└────────────────────────────┬─────────────────────────────┘
                             │ Axios / REST API (JWT Bearer)
┌────────────────────────────▼─────────────────────────────┐
│                 Flask Application Factory                │
│    Blueprints: /api/auth, /api/food, /api/reservations,  │
│          /api/provider, /api/analytics, /api/admin       │
└──────────────┬────────────────────────────┬──────────────┘
               │                            │
   SQLAlchemy Transactions                  │ Dispatches Tasks
   (Row-Level Lock & WAL)                   ▼
┌──────────────▼─────────────┐   ┌─────────────────────────┐
│     SQLite (WAL Mode)      │   │  Celery Worker & Beat   │
│   (foodrescue.db / Docker) │   │     (Redis Broker)      │
│   • users      • listings  │   │  • Auto-Expiration      │
│   • orgs       • reserves  │   │  • Recipient Matching   │
│   • pickups    • impacts   │   │  • Nightly Reports      │
└────────────────────────────┘   └─────────────────────────┘
```

---

## 🚶 Application Walkthrough & User Flows

### Flow 1: Food Provider (Canteen / Bakery)
1. **Sign In**: Log in using provider credentials (or 1-click demo button).
2. **Post Surplus**: Navigate to **Post Surplus Food** (`/create-listing`).
3. **Specify Dietary & Portions**:
   - Select dietary classification (Vegetarian, Non-Veg, Vegan, Bakery).
   - Enter portions (e.g. 50 meals), allergen info, and pickup location.
   - Use quick expiry buttons (`+2 Hours`, `+4 Hours`, `+6 Hours`).
4. **Manage Incoming Requests**: In **My Listings** (`/my-listings`), view live balances and click **View Requests** to approve or decline reservations with 1 click.
5. **Verify Pickup**: In **Verify Pickup** (`/pickup`), enter the recipient's 6-character code upon arrival to confirm food handover.

### Flow 2: Recipient (NGO / Shelter / Volunteer)
1. **Browse Food**: Go to **Browse Food** (`/browse`).
2. **Filter by Diet**: Click one-click filters: **🟢 100% Vegetarian**, **🌱 Pure Vegan**, **🍞 Bakery**, or **🔴 Non-Vegetarian**.
3. **Inspect Countdown & Allergens**: Review remaining portions and live expiration countdown (`⏱️ 2h 15m left`).
4. **Reserve**:
   - Choose requested portions.
   - Review scheduled collection window.
   - Check the mandatory dietary verification checkbox.
5. **Collection Pass**: Open **My Reservations** (`/my-reservations`) to view your **Digital Pickup Pass** with unique verification code (`FR-XXXXXX`).

### Flow 3: Administrator
1. **Sign In**: Sign in with administrator credentials.
2. **Platform Moderation**: Open **Admin Panel** (`/admin`).
3. **Entity Verification**: Review registered restaurants and NGOs and click **Verify Organization** to grant verified trust badges.
4. **Oversight**: Inspect platform metrics and active listing health.

---

## 👥 Pre-Seeded Demo Accounts

The database comes pre-populated with realistic organizations, active surplus listings with live timers, approved reservations, and historical impact records:

| Role | Email | Password | Organization |
| :--- | :--- | :--- | :--- |
| **Provider (Canteen)** | `canteen@foodrescue.org` | `provider123` | University Central Canteen (Chandigarh) |
| **Provider (Bakery)** | `bakery@foodrescue.org` | `provider123` | Golden Crust Artisan Bakery (Chandigarh) |
| **Recipient (Shelter)** | `shelter@foodrescue.org` | `recipient123` | Hope Community Shelter (Chandigarh) |
| **Recipient (NGO)** | `ngo@foodrescue.org` | `recipient123` | Robin Hood Food Army (Chandigarh) |
| **System Admin** | `admin@foodrescue.org` | `admin123` | Platform Administrator |

> [!TIP]
> The **Login Page** features instant **1-Click Demo Buttons** that automatically populate credentials for each role!

---

## 🚀 Getting Started & How to Run

### Prerequisites
- **Python 3.10+** (Tested on Python 3.12)
- **Node.js 18+** & **npm**

---

### Option A: 1-Click Windows Launcher (Fastest)

Run the included development launcher script:
```powershell
.\run_dev.bat
```
This script automatically:
1. Verifies/creates the Python virtual environment.
2. Seeds the database with demo records if not already initialized.
3. Launches the Flask backend on `http://localhost:5001`.
4. Launches the Vue 3 frontend on `http://localhost:5173`.

---

### Option B: Manual Step-by-Step Setup

#### 1. Backend Setup
```powershell
# Create virtual environment
python -m venv backend\venv

# Activate virtual environment (PowerShell)
.\backend\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r backend\requirements.txt

# Seed realistic demo database
python backend\seed_data.py

# Start Flask backend API (runs on port 5001 or 5000)
python backend\run.py
```

#### 2. Frontend Setup
```powershell
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```
Open your browser at **`http://localhost:5173`**.

---

### Option C: Production Docker Compose Deployment

To run the complete production container stack (Flask API, Vue/Nginx, Redis Broker, Celery Worker, Celery Beat scheduler, and persistent SQLite storage):

```powershell
docker-compose up --build
```
- Frontend Web App: `http://localhost:8080`
- Backend API: `http://localhost:5000`
- Redis Broker: `localhost:6379`

---

## ⚙️ Running Celery & Redis Background Jobs

FoodRescue supports dual background scheduling modes:

1. **Local Mode (Zero-Config)**: The Flask application automatically starts an internal `APScheduler` background thread that checks for expired food listings every 60 seconds.
2. **Production Mode (Celery + Redis)**:
   - Ensure Redis is running (e.g., via Docker: `docker run -d -p 6379:6379 redis:7-alpine`).
   - Start the Celery worker:
     ```powershell
     .\run_celery_worker.bat
     ```
   - Start the Celery Beat periodic scheduler:
     ```powershell
     .\run_celery_beat.bat
     ```

---

## 🧪 Automated Testing Suite

Comprehensive automated test coverage verifying concurrency safety, authentication, expiration logic, and carbon calculation:

```powershell
# Run backend pytest suite
backend\venv\Scripts\python -m pytest -v
```

### Verified Test Cases:
- `test_auth_and_registration`: User creation, JWT authentication, and profile querying.
- `test_food_listing_and_concurrency_reservation`:
  - Partial stock reservation (`AVAILABLE` ➔ `PARTIALLY_RESERVED`).
  - Race condition check: Rejection of reservations exceeding remaining quantity with `409 Conflict`.
  - Full stock reservation (`PARTIALLY_RESERVED` ➔ `FULLY_RESERVED`).
  - Cancellation inventory restoration: Restores stock atomically back to the food listing.
- `test_automatic_expiration_engine`: Auto-transitions past-due listings to `EXPIRED` and closes pending reservations.
- `test_pickup_and_impact_metrics`: Pickup verification flow and validation of the `2.5 kg CO₂e / meal` calculation.

---

## 📡 REST API Documentation

### Authentication (`/api/auth`)
- `POST /api/auth/register` — Register a new Provider or Recipient with organization details.
- `POST /api/auth/login` — Authenticate and receive a JWT Bearer token.
- `GET /api/auth/me` — Retrieve current user profile and organization.
- `GET /api/auth/preferences` — Get recipient location and dietary notification preferences.
- `PUT /api/auth/preferences` — Update recipient matching preferences.
- `GET /api/auth/categories` — List all food categories with dietary defaults.

### Food Listings (`/api/food`)
- `GET /api/food` — Filter active surplus donations (supports `search`, `dietary_type`, `category_id`, `city`, `only_active`).
- `GET /api/food/<id>` — Get comprehensive listing details with allergen disclosures.
- `POST /api/food` — Create new surplus food listing (Provider only). Triggers rule-based recipient matching.
- `PUT /api/food/<id>` — Update listing details (Owner Provider or Admin).
- `DELETE /api/food/<id>` — Cancel food listing.

### Reservations & Pickups (`/api`)
- `POST /api/food/<id>/reserve` — Concurrency-safe reservation submission. Atomically deducts inventory.
- `GET /api/reservations` — List current user's reservations.
- `GET /api/reservations/<id>` — Get single reservation details.
- `PUT /api/reservations/<id>/cancel` — Cancel reservation and atomically restore remaining quantity to listing.
- `PUT /api/reservations/<id>/pickup` — Confirm food collection via verification code.

### Provider Operations (`/api`)
- `GET /api/provider/listings` — List all listings posted by current provider with reservation statistics.
- `GET /api/provider/reservations` — View all reservation requests across provider listings.
- `PUT /api/reservations/<id>/approve` — Approve pending reservation request.
- `PUT /api/reservations/<id>/reject` — Decline reservation and return portions back to remaining pool.

### Analytics & Impact (`/api/analytics`)
- `GET /api/analytics/impact` — Platform metrics (meals rescued, active providers, CO₂ avoided).
- `GET /api/analytics/monthly` — Monthly rescued meal distribution for trend charts.
- `GET /api/analytics/categories` — Category breakdown data for doughnut charts.

### Notifications (`/api/notifications`)
- `GET /api/notifications` — List alerts (matching donations, reservation updates, expiration warnings).
- `GET /api/notifications/unread-count` — Count unread alerts for navbar badge.
- `PUT /api/notifications/<id>/read` — Mark single notification as read.
- `PUT /api/notifications/read-all` — Mark all notifications as read.

### Administration (`/api/admin`)
- `GET /api/admin/users` — Audit all registered users and organizations.
- `PUT /api/admin/users/<id>/verify` — Toggle organization verified status.
- `DELETE /api/admin/listings/<id>` — Remove fraudulent or spam listings.
- `GET /api/admin/stats` — Platform-wide health and entity statistics.

---

## 📂 Repository Structure

```
FoodRescue/
├── backend/
│   ├── app/
│   │   ├── __init__.py          # Flask app factory with SQLite WAL pragmas
│   │   ├── config.py            # Development, Testing, and Production configs
│   │   ├── extensions.py        # SQLAlchemy, Migrate, and CORS extensions
│   │   ├── models/              # Domain models (User, Org, Listing, Reservation, Impact)
│   │   │   ├── user.py
│   │   │   ├── food_listing.py
│   │   │   ├── reservation.py
│   │   │   ├── notification.py
│   │   │   └── impact.py
│   │   ├── routes/              # RESTful API Blueprints
│   │   │   ├── auth.py
│   │   │   ├── food.py
│   │   │   ├── reservations.py
│   │   │   ├── provider.py
│   │   │   ├── analytics.py
│   │   │   ├── notifications.py
│   │   │   └── admin.py
│   │   ├── services/            # Core business engines
│   │   │   ├── expiration_service.py
│   │   │   ├── matching_service.py
│   │   │   └── impact_service.py
│   │   ├── tasks/               # Background task architecture
│   │   │   ├── celery_app.py
│   │   │   ├── celery_tasks.py
│   │   │   └── scheduler.py
│   │   └── utils/
│   │       └── auth.py          # JWT authentication and role guards
│   ├── tests/
│   │   └── test_api.py          # Automated pytest test suite
│   ├── seed_data.py             # Realistic database seeder
│   ├── run.py                   # Backend entry point with port conflict detection
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend Docker container
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI components
│   │   │   ├── Navbar.vue
│   │   │   ├── DietaryBadge.vue # Prominent dietary classification component
│   │   │   ├── StatusBadge.vue
│   │   │   ├── CountdownTimer.vue
│   │   │   ├── ReserveModal.vue # Modal with mandatory dietary check
│   │   │   └── StatCard.vue
│   │   ├── views/               # Application view pages
│   │   │   ├── LoginView.vue    # Sign-in with 1-click demo accounts
│   │   │   ├── RegisterView.vue # Role-aware registration
│   │   │   ├── DashboardView.vue# Role-adaptive dashboard
│   │   │   ├── BrowseFoodView.vue # Dietary filters and surplus catalog
│   │   │   ├── FoodDetailView.vue # Full food listing view
│   │   │   ├── CreateListingView.vue # Provider listing creation form
│   │   │   ├── MyListingsView.vue # Provider management table
│   │   │   ├── MyReservationsView.vue # Recipient Digital Pickup Pass
│   │   │   ├── PickupManagementView.vue # Provider verification terminal
│   │   │   ├── NotificationsView.vue # Notification center
│   │   │   ├── ImpactDashboardView.vue # Chart.js environmental analytics
│   │   │   └── AdminDashboardView.vue # Verification and moderation
│   │   ├── stores/              # Pinia state stores (auth, food, notifications)
│   │   ├── services/
│   │   │   └── api.js           # Axios client with JWT interceptors
│   │   ├── router/
│   │   │   └── index.js         # Navigation guards and route definitions
│   │   ├── App.vue
│   │   ├── main.js
│   │   └── style.css            # Tailwind CSS directives
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── Dockerfile               # Multi-stage Frontend Docker container
├── docker-compose.yml           # Production Docker Compose stack
├── run_dev.bat                  # 1-Click Windows development launcher
├── run_celery_worker.bat        # Celery worker launcher
├── run_celery_beat.bat          # Celery beat launcher
├── pytest.ini                   # Pytest configuration
└── README.md                    # Official project documentation
```

---

## 📜 License

Developed as an open-source project contributing towards **UN Sustainable Development Goal 12.3**: *Halving per capita food waste and reducing food losses along production and supply chains*.
