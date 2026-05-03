from datetime import date


def parse_month(s):
    # accepts YYYY-MM string, returns first-of-month date or None
    try:
        y, m = s.split("-")
        return date(int(y), int(m), 1)
    except (ValueError, AttributeError, TypeError):
        return None


def month_bounds(d):
    # returns (start, next_month_start) for half-open range queries
    if d.month == 12:
        nxt = date(d.year + 1, 1, 1)
    else:
        nxt = date(d.year, d.month + 1, 1)
    return d, nxt


def month_options(months_back=24):
    # last N months (current + back), newest first
    today = date.today()
    y, m = today.year, today.month
    out = []
    for _ in range(months_back):
        out.append(date(y, m, 1))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return out


def selected_month(request_get, default=None):
    # convenience for views: read ?month=YYYY-MM, fall back to current
    return parse_month(request_get.get("month")) or (default or _today_month())


def _today_month():
    t = date.today()
    return date(t.year, t.month, 1)
