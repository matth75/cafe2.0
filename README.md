# WebCafe — cafe2.0

WebCafé is a small scheduling website for teaching activities at École normale supérieure Paris-Saclay.
This repository contains the backend API, tests and helper scripts used to manage class schedules and export calendars.

Live site: https://cafe.zpq.ens-paris-saclay.fr

## Overview

- Purpose: manage class schedules (events, rooms, users) and publish per-promotion calendars and CSV exports.
- Audience: currently implemented for the M2Fesup cohort (proof-of-concept / department use).
- Components in this repo:
  - `backend/` — FastAPI backend (API + DB handling)
  - `ics/` — generated or static calendar files used by the service
  - helper scripts at repo root (data import / small DB tools)
  - `tests/` — pytest tests for backend logic and server endpoints

## Backend (how it works)

The backend is a FastAPI application located in the `backend/` folder. Key points:

- Main entry: `backend/server.py` — creates the FastAPI app (root path `/api`), includes routers and small utility endpoints (`/version`, `/classrooms/*`, `/csv`, dynamic `/ics/<promo>` endpoints).
- Database: a local SQLite database (`webcafe.db`) managed by `backend/db_webcafe.py`. The `WebCafeDB` class:
  - Creates and maintains tables: `users`, `events`, `classroom`, `promo`, `meta`.
  - Triggers are used to bump a `meta` `version` value when the `events` table changes — this invalidates cached ICS files so they can be regenerated.
  - Provides helpers for inserting/modifying users and events, generating `.ics` calendar files (via `icalendar`) and CSV exports per promotion.
- Authentication: `backend/dependancies.py` implements JWT token creation/verification and password hashing (Argon2 via `pwdlib`). Token expiration default is 30 minutes.
- Routers: `backend/routers/` contains modular API routers:
  - `users.py` — registration, profile, admin actions (teacher/superuser rights), user listing
  - `ics.py` — endpoints to create/download ICS files and to manage events
  - `app_stats.py` — simple healthcheck/status endpoints

Important behavior:
- Dynamic ICS endpoints are generated at startup from the `promo` SQL table; cached .ics files live in an `ics/` folder and are regenerated when `meta.version` changes.
- CORS is enabled in `server.py` — in development it should allow local frontend origins; in production it must be restricted to your frontend domain.

## Frontend

This project includes a separate frontend (built with Node.js) that provides the graphical interface. The frontend is served separately (build files are deployed alongside the backend/Nginx configuration). The frontend calls the backend API under `/api` (e.g. `https://cafe.zpq.ens-paris-saclay.fr/api`).

For frontend specific instructions, please refer to the FRONTEND.md file in the frontend folder.

## Running the backend (quick start)

To setup and run the backend, and for more backend specific explanations, please refer to the BACKEND.md file located in the backend folder.


## Hosting (Raspberry Pi + Nginx + Certbot)

The live site runs on a Raspberry Pi behind Nginx acting as a reverse proxy. High-level steps used in deployment:

1. Deploy backend on the Pi and run the FastAPI app (systemd service or a process supervisor to keep it running).
2. Configure Nginx to:
   - serve the frontend static build files
   - reverse-proxy API requests to the backend (e.g. `location /api/` -> `http://127.0.0.1:8000/api/`).
3. Use Certbot to obtain and renew TLS certificates (Let's Encrypt) and enable HTTPS for the domain (`https://cafe.zpq.ens-paris-saclay.fr`).

Minimal Nginx notes:

- Ensure `proxy_set_header Host $host;` and `proxy_set_header X-Real-IP $remote_addr;` are set for proxied API routes.
- Redirect HTTP to HTTPS and enable strong TLS settings per Certbot recommendations.

## Tests

There is a `tests/` folder with pytest tests covering `db_webcafe` logic and some server endpoints. Please refer to the TESTS.md file for more test specific instructions.

## Useful files and scripts

- `add_ods_into_SQL.py`, `fill_xls.py` — helper scripts to populate the events table from spreadsheet sources
- `small_db.py` — utilities for creating or inspecting a small local DB for testing
- `ics/` — contains `all.ics` and other ICS-related sidecar files used to cache generated calendars

## Security and deployment notes

- In production, restrict CORS origins in `backend/server.py` to your frontend domain and set `allow_credentials` appropriately.
- Keep the JWT `SECRET_KEY` (in `backend/dependancies.py`) secret — move it to environment variables in production.

## Contact / Credits

Implemented though the Génie Logiciel course from the INTRANET M2FESup (ENS Paris-Saclay) Authors : Mathieu Guerin, Pierre-Louis Filoche, Matthieu Rouet. (promo 2025/2026)

 For questions about deployment or development, feel free to reach out to us !

---


