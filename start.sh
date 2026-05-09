#!/usr/bin/env bash
# Monex bootstrap — venv, deps, migrate, seed, run

set -e

GOLD='\033[38;5;220m'
RED='\033[38;5;196m'
DIM='\033[2;38;5;220m'
RST='\033[0m'

cd "$(dirname "$0")"

echo -e "${GOLD}// Monex · bootstrap${RST}"

# check for existing db — ask before nuking it
DB="db.sqlite3"
if [ -f "$DB" ]; then
  echo -e "${DIM}> existing database detected${RST}"
  echo -e "${DIM}> first_run wizard handles email & admin setup${RST}"
  echo -e "${DIM}> to start completely fresh, delete ${DB} and re-run${RST}"
fi

# venv
if [ ! -d ".venv" ]; then
  echo -e "${DIM}> creating venv...${RST}"
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# deps
echo -e "${DIM}> installing deps...${RST}"
pip install -q --disable-pip-version-check -r requirements.txt

# env file
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo -e "${DIM}> created .env from template${RST}"
fi

# migrate
python main.py migrate --no-input

# seed defaults (idempotent)
python main.py seed_defaults

echo ""
echo -e "${GOLD}// system online${RST}"
echo -e "${GOLD}// http://localhost:8000  ·  first_run wizard at /accounts/first-run/${RST}"
echo ""

python main.py runserver
