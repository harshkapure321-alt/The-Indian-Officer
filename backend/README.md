# The Indian Officer (TIO) — Backend

FastAPI + PostgreSQL + SQLAlchemy 2.0 (sync) + Alembic. JWT auth, bcrypt, UUID primary keys.

## Status

Built so far (Step 1 — Foundation):

- Project structure, settings from environment variables
- All database models (users, subjects, topics, concepts, cases, evidence, investigation sessions,
  responses, hints, mistake notebook, progress, concept mastery, documents)
- Auth: register / login / refresh / me (bcrypt + JWT access & refresh tokens)
- Subjects and topics APIs, topic → published cases (answer keys never returned)
- Consistent `{success, data, message}` response envelope and safe error handlers
- Geography seed (9 learning categories, all marked **not academically validated**)
- Pytest suite for the above

Not built yet: case/evidence/investigation endpoints, Discovery & Revision engines, evaluation,
mistake notebook, analytics, TIO AI, document upload, D-001 / R-001 case data.

## Setup

Requires Python 3.11+ and PostgreSQL 14+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 1. Create the database

```bash
psql -U postgres
```
```sql
CREATE USER tio_user WITH PASSWORD 'choose-a-strong-password';
CREATE DATABASE tio_db OWNER tio_user;
\q
```

### 2. Configure environment

```bash
cp .env.example .env
```
Edit `.env`: set the password inside `DATABASE_URL` and generate a `SECRET_KEY`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

### 3. Create the tables (Alembic)

The initial migration has not been generated yet because it must be produced against your
installed library versions. Generate it once, review it, then apply it:

```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
```

Commit the generated file in `migrations/versions/`. All future schema changes go through Alembic.

### 4. Seed Geography

```bash
python -m app.utils.seed_geography
```

### 5. Run

```bash
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

In Swagger, call `POST /api/v1/auth/login`, copy `access_token`, click **Authorize**, and paste it.

## Tests

Tests run on an in-memory SQLite database (no PostgreSQL needed) and force their own settings,
so they can never touch your real database.

```bash
pytest -v
```

## Response format

```json
{ "success": true, "data": { }, "message": "" }
```
Errors use the same shape with `"success": false` and `"data": null` (validation errors put a
list of `{field, message}` under `data.errors`).

## Security notes

- Passwords hashed with bcrypt (max 72 bytes, enforced at validation).
- Access tokens (30 min) and refresh tokens (7 days) are separate types; one cannot be used as the other.
- Login gives the same error for unknown email and wrong password.
- Register cannot set a role. Users start as `student`.
- `answer_key`, `evaluation_rubric`, `case_content` and document file paths are never in public schemas.
- Never commit `.env` or `uploads/` contents.
