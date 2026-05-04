# MonEX

personal expense tracker. django + sqlite, themed after deus ex: human revolution.

## quick start

```bash
chmod +x start.sh
./start.sh
```

then hit http://localhost:8000 — login `admin` / `admin`.

`start.sh` handles everything: creates the venv, installs deps, copies `.env`, runs migrations, seeds default banks/categories, creates the admin user, and starts the dev server.

## features

- monthly dashboard with kpi cards, charts, savings rate gauge
- transactions: add / edit / delete, csv + pdf monthly extract
- analytics: 12-month trend, day-of-week patterns, category evolution, top categories
- recurring bills/subscriptions with per-month paid/received tracking
- per-category and overall monthly budgets, red warning when over
- single-tenant auth, change passcode, password reset
- htmx + alpine.js + chart.js + three.js, no spa heaviness

## stack

- python 3.12+, django 6
- sqlite via `dj-database-url` (swap to postgres by setting `DATABASE_URL`)
- htmx + alpine.js + chart.js + three.js (cdn)
- weasyprint for pdf
- handwritten css

## manual setup (if you'd rather not use start.sh)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python main.py migrate
python main.py setup_admin       # creates admin / admin
python main.py seed_defaults     # banks + categories
python main.py runserver
```

## env vars

| var | default | notes |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev fallback | set this in prod |
| `DJANGO_DEBUG` | `1` | `0` for prod |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | comma-separated |
| `DATABASE_URL` | sqlite | swap to postgres if needed |
| `ADMIN_USERNAME` | `admin` | seeded by setup_admin |
| `ADMIN_PASSWORD` | `admin` | seeded by setup_admin |

## license

mit
