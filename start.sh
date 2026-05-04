#!/usr/bin/env bash
# Monex bootstrap - venv, deps, migrate, seed, admin, run

set -e

GOLD='\033[38;5;220m'
DIM='\033[2;38;5;220m'
RST='\033[0m'

cd "$(dirname "$0")"

echo -e "${GOLD}// Monex · bootstrap${RST}"

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

# create admin/admin (idempotent)
ADMIN_USERNAME=admin ADMIN_PASSWORD=admin python main.py setup_admin

echo ""
echo -e "${GOLD}// system online${RST}"
echo -e "${GOLD}// http://localhost:8000  ·  admin / admin${RST}"
echo ""

python main.py runserver
