
<div align="center">
<img src="icon.png" width="72">
<br>

**<code>// M O N E X</code>**

#### **personal expense tracker** · django 6 · sqlite · python  · alpinejs · deus ex HR inspired

[![Stars](https://img.shields.io/github/stars/ARCANGEL0/Monex?style=for-the-badge&color=0a0a0a&labelColor=0a0a0a&logo=github&logoColor=fad27a)]()
[![Watchers](https://img.shields.io/github/watchers/ARCANGEL0/Monex?style=for-the-badge&color=0a0a0a&labelColor=0a0a0a&logo=eye&logoColor=fad27a)]()
[![Forks](https://img.shields.io/github/forks/ARCANGEL0/Monex?style=for-the-badge&color=0a0a0a&labelColor=0a0a0a&logo=git&logoColor=fad27a)]()
[![Django](https://img.shields.io/badge/DJANGO_6-fad27a?style=for-the-badge&labelColor=0a0a0a&logo=django&logoColor=0a0a0a)]()

![GitHub issues](https://img.shields.io/github/issues/ARCANGEL0/Monex?style=for-the-badge&color=fad27a&labelColor=0a0a0a)
![GitHub pull requests](https://img.shields.io/github/issues-pr/ARCANGEL0/Monex?style=for-the-badge&color=fad27a&labelColor=0a0a0a)
![GitHub last commit](https://img.shields.io/github/last-commit/ARCANGEL0/Monex?style=for-the-badge&color=fad27a&labelColor=0a0a0a)

</div>

---

 ## ⬡ 𝗔𝗯𝗼𝘂𝘁 𝗠𝗼𝗻𝗲𝘅 

MonEx is my personal finance management dashboard built with Django, featuring comprehensive transaction tracking, recurring bill management to track paid and unpaid subs, budget enforcement under a monthly cap, and detailed spending analytics. The interface provides monthly KPIs, savings metrics, category breakdowns, and trend analysis through interactive charts. Built with HTMX and Alpine.js for a responsive single-page dashboard without the overhead of a JavaScript framework. Supports SQLite and PostgreSQL, with CSV and PDF export capabilities aswell. UI heavily inspired in Deus Ex: HR.

 
 <h2>➤ Features </h2> 

- **Dashboard** 𐰷 Monthly kpi cards, savings rate gauge, recent transactions
- **Transactions** 𐰷 Add / edit / delete, csv + pdf extract per month
- **Analytics** 𐰷 Graphs with 12-month trends, day-of-week patterns, category evolution, top categories 
- **Recurring** 𐰷 Bills and subscriptions with paid/received tracking, auto-materialize into transactions
- **Budgets** 𐰷 Per-category and global monthly caps with over-budget warnings
- **Auth** 𐰷 Single-tenant, passcode change, password reset, full midleware working (Needs SMTP setup with gmail)


<h2>🞛 Quick Start </h2>

To start MonEx, run the initiator script to open the setup page and configure SMTP.

```bash
chmod +x first_run.sh
./first_run.sh
```

It will ask you to setup a gmail and app password to be used as MonEx email middleware, after setting up the Email, you will create a master account to login and start using MonEx.

For general server start, use `.start.sh` 

```bash
chmod +x start.sh
# the script builds the venv, installs deps, runs migrations, seeds banks & categories, creates the admin user, and starts the UI.
./start
```

<details> 
  <summary> <h4> Manual setup</h4></summary>

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python main.py migrate
python main.py setup_admin       # creates admin / admin
python main.py seed_defaults     # banks + categories
python main.py runserver
```
</details>


 <h2>⛛ Stack </h2> 
 
| Layer | Choice |
|---|---|
| Backend | Python 3.12+, Django 6 |
| Database | SQLite (swap to postgres via `DATABASE_URL`) |
| Frontend | HTMX + Alpine.js 𐰷 no spa |
| Visuals | Chart.js, Three.js, WeasyPrint (for pdf) |
| CSS | TailwindCSS-like & custom inspiration in Deus Ex. |

 
  <h2>ㅿ Env Vars  </h2> 

| Var | Default | Note |
|---|---|---|
| `DJANGO_SECRET_KEY` | dev fallback | Set in prod |
| `DJANGO_DEBUG` | `1` | `0` in prod |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-sep |
| `DATABASE_URL` | sqlite | Postgres if needed |
| `ADMIN_USERNAME` | `admin` | setup_admin seed |
| `ADMIN_PASSWORD` | `admin` | setup_admin seed |

 

 <h2>⍚ License</h2> 

 <details>
<summary><h4>MIT License</h4></summary>
  
```
Copyright (c) 2026 MonEx - Finance Tracker

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
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

**[[ꋧ]](#personal-expense-tracker--django-6--sqlite--python---alpinejs--deus-ex-hr-inspired)**

</div>
