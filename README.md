# Finance Data Processing and Access Control Backend

> A secure, production-quality Django REST API for finance data processing with role-based access control, dashboard analytics, and comprehensive API documentation.

**Built for:** Zorvyn Backend Developer Intern Assignment  
**Author:** Kshitiz  

---

## 🚀 Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| Python | 3.11.8 | Runtime |
| Django | 5.2.12 | Web framework |
| Django REST Framework | 3.17.1 | API toolkit |
| SimpleJWT | 5.5.1 | JWT authentication |
| drf-spectacular | 0.29.0 | OpenAPI / Swagger docs |
| django-jazzmin | 3.0.4 | Admin panel theming |
| django-cors-headers | 4.9.0 | CORS support |
| SQLite | 3 | Database (ships with Python) |

## 🌟 Key Features

### 1. Dual Interface (API + Custom Frontend)
- **Role-Based Web Dashboard:** A stunning, responsive dark/light mode dashboard built with HTML/CSS and Chart.js.
  - *Viewers* see the transaction ledger with a running balance.
  - *Analysts & Admins* see rich visualizations (burn rate, savings rate, income vs. expense doughnut chart, and monthly cash flow trends).
- **Secure API Backend:** A fully functioning Django REST Framework providing JWT authentication and endpoints for all dashboard data.

### 2. Deep Finance Analytics
- **Double-Entry Ledger:** Transactions are tracked with a real-time running balance.
- **KPI Metrics:** Automatically calculates Savings Rate, Expense Ratio, Income Growth, and overall Net Balance.
- **Top Categories:** Breakdowns of where money is entering and leaving.

### 3. Role-Based Access Control (RBAC)
- **Admin:** Full CRUD access, can create transactions, and manage users via the admin panel.
- **Analyst:** Can view all transactions and analytics insights, but cannot write or modify records.
- **Viewer:** Read-only access to basic transaction records.

---

## 📁 Project Structure

```
Zorvyn/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3                    # SQLite database (auto-created)
│
├── finance_project/              # Django project configuration
│   ├── settings.py               # All settings (DB, JWT, CORS, security, etc.)
│   ├── urls.py                   # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
│
└── api/                          # Main application
    ├── models.py                 # User (with roles), Transaction models
    ├── serializers.py            # Request/response serializers with validation
    ├── permissions.py            # RBAC: IsAdmin, IsAnalystOrAdmin, IsAnyAuthenticatedRole
    ├── pagination.py             # Custom pagination (configurable page size)
    ├── utils.py                  # Custom exception handler
    ├── admin.py                  # Enhanced admin panel config
    │
    ├── views/                    # API views (separated by domain)
    │   ├── root_view.py          # API welcome page
    │   ├── auth_views.py         # Registration
    │   ├── transaction_views.py  # Transaction CRUD ViewSet
    │   ├── dashboard_views.py    # Analytics endpoints
    │   └── user_views.py         # User management (admin only)
    │
    ├── services/                 # Business logic layer
    │   ├── dashboard_service.py  # Analytics computations
    │   └── transaction_service.py# Filtering, search, soft delete
    │
    ├── management/commands/      # Custom management commands
    │   └── seed_data.py          # Demo data seeder
    │
    ├── tests/                    # Unit & integration tests
    │   ├── test_auth.py          # Authentication tests
    │   ├── test_transactions.py  # Transaction CRUD + RBAC tests
    │   └── test_dashboard.py     # Dashboard analytics tests
    │
    └── urls.py                   # API URL routing
```

---

## ⚡ Quick Start

### Option A: Windows One-Click Setup
If you are on Windows, simply double-click the included batch file to automate everything from virtual environment creation to starting the server:

```bash
# Just run this file
setup.bat
```
*(This will setup Python, install requirements, migrate the database, seed demo data, and start the local server on port 8000 automatically).*

---

### Option B: Manual Setup

#### 1. Clone & Setup

```bash
git clone <repo-url>
cd Zorvyn

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py makemigrations api
python manage.py migrate
```

### 3. Seed Demo Data

```bash
python manage.py seed_data
```

This creates:
- **3 users** with predefined roles and passwords
- **50+ transactions** across 6 months of realistic financial data

| Username | Password | Role |
|---|---|---|
| `admin_user` | `Admin@123` | Admin |
| `analyst_user` | `Analyst@123` | Analyst |
| `viewer_user` | `Viewer@123` | Viewer |

### 4. Create Superuser (for Django Admin)

```bash
python manage.py createsuperuser
```

### 5. Run Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 📌 API Endpoints

### Authentication
| Method | Endpoint | Access | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | Public | Register new user |
| POST | `/api/auth/token/` | Public | Login (returns JWT tokens) |
| POST | `/api/auth/token/refresh/` | Public | Refresh access token |

### Transactions
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/transactions/` | All roles | List (with filtering & search) |
| POST | `/api/transactions/` | Admin | Create transaction |
| GET | `/api/transactions/{id}/` | All roles | Retrieve single |
| PUT/PATCH | `/api/transactions/{id}/` | Admin | Update |
| DELETE | `/api/transactions/{id}/` | Admin | Soft delete |

**Supported query parameters:**
- `?type=income` or `?type=expense`
- `?category=groceries` (case-insensitive)
- `?date_from=2026-01-01&date_to=2026-03-31`
- `?search=salary` (searches description & category)
- `?page=2&page_size=20`

### Dashboard Analytics
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/dashboard/summary/` | Analyst/Admin | Income, expenses, net balance |
| GET | `/api/dashboard/categories/` | Analyst/Admin | Category breakdown |
| GET | `/api/dashboard/trends/` | Analyst/Admin | Monthly trends |
| GET | `/api/dashboard/recent/` | Analyst/Admin | Recent activity |
| GET | `/api/dashboard/top-categories/` | Analyst/Admin | Top income/expense categories |

### User Management
| Method | Endpoint | Access | Description |
|---|---|---|---|
| GET | `/api/users/` | Admin | List all users |
| GET/PUT/PATCH | `/api/users/{id}/` | Admin | View/update user role & status |

### Documentation
| URL | Description |
|---|---|
| `/api/docs/` | Swagger UI |
| `/api/redoc/` | ReDoc |
| `/api/schema/` | OpenAPI schema (JSON) |
| `/admin/` | Django Admin Panel |

---

## 🔐 Role-Based Access Control (RBAC)

| Action | Viewer | Analyst | Admin |
|---|---|---|---|
| View transactions | ✅ | ✅ | ✅ |
| Search/filter transactions | ✅ | ✅ | ✅ |
| View dashboard analytics | ❌ | ✅ | ✅ |
| Create transactions | ❌ | ❌ | ✅ |
| Update transactions | ❌ | ❌ | ✅ |
| Delete transactions | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |

Three custom permission classes enforce this:
- `IsAdmin` — only `admin` role
- `IsAnalystOrAdmin` — `analyst` or `admin` roles
- `IsAnyAuthenticatedRole` — any authenticated user

---

## 🛡️ Security Features

- **JWT Authentication** — Stateless token-based auth with SimpleJWT
- **Token Rotation** — Refresh tokens are rotated and blacklisted after use
- **Rate Limiting** — DRF throttling (30/min anonymous, 120/min authenticated)
- **CORS** — Configured with `django-cors-headers`
- **Security Headers** — X-Content-Type-Options, X-Frame-Options, XSS protection
- **HSTS** — Enabled in production mode
- **Input Validation** — Amount must be positive, dates can't be future, email uniqueness
- **Soft Delete** — Records are never permanently deleted via API
- **Password Validation** — Django's built-in validators (min length, common passwords, etc.)
- **Custom Error Responses** — Consistent error format across all endpoints

---

## 🧪 Running Tests

```bash
python manage.py test api
```

**Test coverage includes:**
- ✅ Registration (success, duplicate, weak password, missing fields)
- ✅ Login (success, wrong password, nonexistent user)
- ✅ Token refresh (valid/invalid tokens)
- ✅ Transaction CRUD (create, update, soft delete)
- ✅ RBAC enforcement (viewer/analyst blocked from writes)
- ✅ Filtering (by type, category, date range)
- ✅ Search (description and category)
- ✅ Input validation (negative amounts, future dates, invalid types)
- ✅ Dashboard analytics (correct totals, soft-delete exclusion)
- ✅ Dashboard RBAC (viewer blocked, analyst/admin allowed)

---

## 🏗️ Architecture & Design Decisions

### Separation of Concerns
- **Models** → Data definition and database schema
- **Serializers** → Request validation and response formatting
- **Permissions** → Access control logic (RBAC)
- **Services** → Business logic (filtering, analytics, soft delete)
- **Views** → HTTP request handling (thin layer, delegates to services)

### Why Django + DRF?
- **Batteries-included** — Admin panel, ORM, migrations, auth out of the box
- **Battle-tested** — SimpleJWT handles token lifecycle properly
- **Rich ecosystem** — Jazzmin for admin UI, drf-spectacular for docs

### Trade-offs
- **SQLite** — Chosen for simplicity and zero-config setup. For production, would use PostgreSQL.
- **Soft delete** — Implemented via `is_deleted` flag rather than a separate archive table, keeping the schema simple.
- **Rate limiting** — Using DRF's built-in throttling for simplicity. For production, would use Redis-backed solution.

---

## 📝 Assumptions

1. All monetary amounts are in a single currency (INR)
2. Transaction dates cannot be in the future
3. Users self-register as `viewer` by default; admins upgrade roles
4. Soft-deleted records are excluded from all API responses and analytics
5. Dashboard analytics are computed in real-time (acceptable for SQLite scale)

---

## 📄 License

This project was built as an assignment submission for Zorvyn.
