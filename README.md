# MonEX

personal expense tracker. django + sqlite, themed after deus ex: human revolution (black metallic + gold). single-user.

## features

- monthly dashboard with income/expense/net/savings rate
- transactions page with add/edit/delete, csv + pdf monthly extract
- analytics: trends, day-of-week patterns, category evolution
- recurring bills/subscriptions with auto-materialization
- per-category and overall monthly budgets, red warning when over
- htmx + alpine.js, no spa heaviness

## stack

- python 3.12+, django 5
- sqlite via `dj-database-url` (swap to postgres by changing `DATABASE_URL`)
- htmx + alpine.js + chart.js (cdn)
- weasyprint for pdf
- handwritten css, no tailwind

## getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py setup_admin       # creates admin / changeme
python manage.py seed_defaults     # seed banks + categories
python manage.py runserver
```

then hit http://localhost:8000 — login `admin` / `changeme`.

## deploy

runs as a systemd service behind cloudflare tunnel. see deploy notes (separate repo).

## license

mit
