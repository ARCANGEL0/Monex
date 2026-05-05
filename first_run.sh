#!/usr/bin/env bash
set -e

CYAN='\033[0;36m'
GOLD='\033[0;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}// MonEx — first run bootstrap${NC}"
echo ""

cd "$(dirname "$0")"

echo -e "${GOLD}[1/4] preparing environment...${NC}"
rm -rf .venv
python3 -m venv .venv

# Arch sometimes strips pip from venvs — reinstall if missing
if [ ! -f ".venv/bin/pip" ]; then
  .venv/bin/python -m ensurepip --upgrade 2>/dev/null
fi

.venv/bin/python -m pip install -q --upgrade pip 2>/dev/null

echo -e "${GOLD}[2/4] installing dependencies...${NC}"
.venv/bin/pip install -q -r requirements.txt

if [ ! -f ".env" ]; then
  echo -e "${GOLD}[3/4] creating .env from template...${NC}"
  cp .env.example .env
else
  echo -e "${GREEN}[3/4] .env found${NC}"
fi

# check for existing data
HAS_DATA=false
REASON=""

if [ -f "db.sqlite3" ]; then
  SUPER_COUNT=$(.venv/bin/python main.py shell -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expensetracker.settings')
django.setup()
from django.contrib.auth import get_user_model
print(get_user_model().objects.filter(is_superuser=True).count())
" 2>/dev/null || echo "0")
  if [ "$SUPER_COUNT" -gt 0 ] 2>/dev/null; then
    HAS_DATA=true
    REASON="primary operator account exists"
  fi
fi

if [ "$HAS_DATA" = false ]; then
  SMTP_USER=$(grep -E "^EMAIL_HOST_USER=.+" .env 2>/dev/null | head -1 | cut -d= -f2)
  if [ -n "$SMTP_USER" ]; then
    HAS_DATA=true
    REASON="smtp credentials configured"
  fi
fi

if [ "$HAS_DATA" = true ]; then
  echo -e "${RED}// MonEx has previous data: ${REASON}${NC}"
  echo -e "${GOLD}// erase and register a new primary operator? (y/n)${NC}"
  read -r CONFIRM
  CONFIRM=$(echo "$CONFIRM" | tr '[:upper:]' '[:lower:]')
  if [ "$CONFIRM" = "y" ] || [ "$CONFIRM" = "yes" ]; then
    echo -e "${GOLD}  > wiping database...${NC}"
    rm -f db.sqlite3
    echo -e "${GOLD}  > clearing smtp credentials...${NC}"
    sed -i 's/^EMAIL_HOST_USER=.*/EMAIL_HOST_USER=/' .env
    sed -i 's/^EMAIL_HOST_PASSWORD=.*/EMAIL_HOST_PASSWORD=/' .env
    echo -e "${GREEN}  > clean slate ready${NC}"
  else
    echo -e "${CYAN}// keeping existing data. exiting.${NC}"
    exit 0
  fi
fi

echo -e "${GOLD}[4/4] running migrations...${NC}"
.venv/bin/python main.py migrate --no-input
.venv/bin/python main.py seed_defaults

echo ""
echo -e "${CYAN}// bootstrap complete${NC}"
echo -e "${GOLD}  → starting dev server...${NC}"
echo ""

(sleep 2 && xdg-open http://127.0.0.1:8000/ 2>/dev/null || open http://127.0.0.1:8000/ 2>/dev/null || true) &

exec .venv/bin/python main.py runserver 127.0.0.1:8000
