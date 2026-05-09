
<div align="center">
<img src="icon.png" width="72">
<br>

**<code>// M O N E X</code>**

**personal expense tracker** · django 6 · sqlite · deus ex themed

[![Stars](https://img.shields.io/github/stars/ARCANGEL0/Monex?style=for-the-badge&color=353535)]()
[![Watchers](https://img.shields.io/github/watchers/ARCANGEL0/Monex?style=for-the-badge&color=353535)]()
[![Forks](https://img.shields.io/github/forks/ARCANGEL0/Monex?style=for-the-badge&color=353535)]()
[![Repo Views](https://komarev.com/ghpvc/?username=Monex&color=353535&style=for-the-badge&label=REPO%20VIEWS)]()
[![AI](https://img.shields.io/badge/stack-Django_6-cyan.svg?style=for-the-badge)]()
![Version](https://img.shields.io/badge/version-1.0-blue?style=for-the-badge&color=d4af37)

![GitHub issues](https://img.shields.io/github/issues/ARCANGEL0/Monex?style=for-the-badge&color=3f3972)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ARCANGEL0/Monex?style=for-the-badge&color=3f3972)
![GitHub last commit](https://img.shields.io/github/last-commit/ARCANGEL0/Monex?style=for-the-badge&color=3f3972)

</div>

---

<details>
<summary><h2>⬡ 𝗔𝗯𝗼𝘂𝘁 𝗠𝗼𝗻𝗲𝘅</h2></summary>

Transaction tracker, budget manager, analytics dashboard — wrapped in a single-tenant django app with a gold-and-black deus ex: human revolution coat of paint. No saas, no javascript framework churn, just a server-rendered dashboard that works.

</details>

<details>
<summary><h2>⟢ Features .ᐟ</h2></summary>

- **Dashboard** — Monthly kpi cards, savings rate gauge, recent transactions
- **Transactions** — Add / edit / delete, csv + pdf extract per month
- **Analytics** — 12-month trends, day-of-week patterns, category evolution, top categories
- **Recurring** — Bills and subscriptions with paid/received tracking, auto-materialize into transactions
- **Budgets** — Per-category and global monthly caps with over-budget warnings
- **Auth** — Single-tenant, passcode change, password reset

</details>

<details>
<summary><h2>⟢ Quick Start .ᐟ</h2></summary>

```bash
chmod +x start.sh
./start.sh
```

Opens at http://localhost:8000 — login `admin` / `admin`.

`start.sh` builds the venv, installs deps, runs migrations, seeds banks & categories, creates the admin user, and starts gunicorn.

### Manual setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py migrate
python main.py setup_admin
python main.py seed_defaults
python main.py runserver
```

</details>

<details>
<summary><h2>⟢ Stack .ᐟ</h2></summary>

| Layer | Choice |
|---|---|
| Backend | Python 3.12+, Django 6 |
| Database | SQLite (swap to postgres via `DATABASE_URL`) |
| Frontend | HTMX + Alpine.js — no spa |
| Visuals | Chart.js, Three.js (hero), WeasyPrint (pdf) |
| CSS | Handwritten, gold & black theme |

</details>

<details>
<summary><h2>⟢ Env Vars .ᐟ</h2></summary>

| Var | Default | Note |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev fallback | Set in prod |
| `DJANGO_DEBUG` | `1` | `0` in prod |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-sep |
| `DATABASE_URL` | sqlite | Postgres if needed |
| `ADMIN_USERNAME` | `admin` | setup_admin seed |
| `ADMIN_PASSWORD` | `admin` | setup_admin seed |

</details>

<details>
<summary><h2>🗈 Project Note</h2></summary>

```
I got tired of spreadsheets. Every month I'd open the same libreoffice file, 
manually categorize my expenses, and try to figure out where all my money went. 
There are plenty of expense trackers out there, but they're either SaaS with 
a monthly fee, or they look like they belong in a 2008 ERP system.

So I built this. Django because it's boring and reliable. HTMX because I didn't 
want to write a SPA for a single-user app. And the deus ex theme because if I'm 
going to stare at a dashboard every day, it might as well look cool.

Gold on black. No tracking. No subscription. Just a django app that tracks 
where your money goes.
```

</details>

<div align="center">

### ❤️ Support

[![Star on GitHub](https://img.shields.io/github/stars/ARCANGEL0/Monex?style=social)]()
[![Follow on GitHub](https://img.shields.io/github/followers/ARCANGEL0?style=social)]()
<br>

<a href='https://ko-fi.com/J3J7WTYV7' target='_blank'><img height='36' style='border:0px;height:36px;' src='https://storage.ko-fi.com/cdn/kofi3.png?v=6' border='0' alt='Buy Me a Coffee at ko-fi.com' /></a>
<br>
<strong>Hack the world. Byte by byte.</strong> ⛛
<br>

**[[ꋧ]](#)**

</div>
