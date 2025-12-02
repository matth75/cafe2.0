# WebCafe Backend

FastAPI-based backend server for the WebCafe scheduling system, managing users, classrooms, events, and calendar exports.

## Quick Start

### Install Dependencies

Python librairies that need to be installed can be found in the `requierements.txt` file. Use the following commands 
(inside a virtual environment) to install the requiered Python packages.

Using **pip**:
```bash
pip install -r requirements.txt
```

Using **conda**:
```bash
conda install -f requirements.txt
```

Using **mamba** (recommended for faster performance):
```bash
mamba install -f requirements.txt
```

> **Note:** [Mamba](https://mamba.readthedocs.io/en/latest/) is a faster drop-in replacement for conda. 
If you haven't installed it yet, we recommend you check the [installation guide](https://mamba.readthedocs.io/en/latest/installation/mamba-installation.html).

### Run the Server

From the project root directory, run the following command for production mode:

```bash
fastapi run backend/server.py
```

#### Options

- **Development mode** (with auto-reload (*)):
  ```bash
  fastapi dev backend/server.py 
  ```

- **Specify a custom port** (default is 8000):
  ```bash
  fastapi dev backend/server.py --port 8080
  ```


(*) : every time one file is saved, the fastapi server will reload with your changes automatically ! Useful for testing !

The API is available at `http://localhost:8000/api` (or your specified port) with FastAPI docs at `http://localhost:8000/api/docs`. Use the FastAPI docs for debugging !

## Module Structure

```
backend/
├── server.py              # Main FastAPI application entry point
├── db_webcafe.py          # SQLite database handler (WebCafeDB class)
├── dependancies.py        # Authentication utilities (JWT, password hashing)
├── routers/
│   ├── users.py           # User management endpoints
│   ├── ics.py             # ICS file handling endpoints
│   └── app_stats.py       # Health check and status endpoints
└── requirements.txt       # Python dependencies
```

### File Descriptions

- **`server.py`** — Main FastAPI application entry point. Initializes the app, includes routers, and defines core endpoints for calendar/CSV exports and user permissions.
- **`db_webcafe.py`** — SQLite database handler (`WebCafeDB` class). Contains all read/write operations, ICS generation, and CSV export logic.
- **`dependancies.py`** — Authentication utilities: JWT token creation/validation, password hashing (Argon2), and user authentication.
- **`routers/users.py`** — User management (registration, login, profile updates, list users if superuser)
- **`routers/ics.py`** — ICS file handling (event creation/deletion, dynamic calendar generation per promotion)
- **`routers/app_stats.py`** — Health check and server status endpoints

## Database Schema

**SQLite database:** `webcafe.db`

### Tables

| Table | Columns | Purpose |
|-------|---------|---------|
| **users** | `id`, `login`, `email`, `nom`, `prenom`, `hpwd`, `birthday`, `promo_id`, `teacher`, `superuser`, `noteKfet` | User accounts with roles (teacher, superuser) and promotion affiliation |
| **events** | `event_id`, `start`, `end`, `matiere`, `type_cours`, `infos_sup`, `classroom_id`, `user_id`, `promo_id` | Course events with scheduling, location, and subject information |
| **classroom** | `classroom_id`, `location`, `capacity`, `type` | Physical classroom definitions (capacity, type: TP/CM/Exam/Lab) |
| **promo** | `promo_id`, `promo_name` | Academic promotions (cohorts) |
| **meta** | `key`, `version`, `last_modified` | Metadata for cache invalidation; tracks `events` version for ICS regeneration |

**Triggers:** Automatic version bumping on `events` table modifications (insert/update/delete) to invalidate cached ICS files.

## Key Features

- **JWT Authentication** — Secure login with 30-minute token expiration
- **Role-based Access** — Teachers and superusers have elevated privileges
- **Dynamic ICS Calendars** — Per-promotion calendar exports with automatic regeneration on data changes
- **CSV Export/import** — Event data export by promotion

## Testing

The `file add_ods_into_SQL.py` populates the events table from webcafe.db with default events, found in the `all_events.xlsx file`. Useful for testing !