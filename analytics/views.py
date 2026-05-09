import json
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Exists, OuterRef, Sum
from django.db.models.functions import ExtractIsoWeekDay, ExtractDay, TruncMonth
from django.shortcuts import redirect, render

from core.utils import month_bounds, month_options, selected_month
from recurring.models import RecurringTransaction
from transactions.models import Transaction

TREND_MONTHS = 12
TOP_CATS = 8
DEFAULT_COLOR = "#7a7466"


def _htmx(request):
    return bool(request.headers.get("HX-Request"))


def _months_range(n=TREND_MONTHS):
    today = date.today()
    y, m = today.year, today.month
    out = []
    for _ in range(n):
        out.insert(0, date(y, m, 1))
        m -= 1
        if m == 0:
            m = 12
            y -= 1
    return out


def _to_date(v):
    return v.date() if hasattr(v, "date") else v


def home(request):
    if not _htmx(request):
        return redirect("core:root")
    months = _months_range()
    sel = selected_month(request.GET, default=months[-1])
    start, end = month_bounds(sel)

    qs = Transaction.objects.filter(owner=request.user, occurred_on__gte=start, occurred_on__lt=end)
    all_qs = Transaction.objects.filter(owner=request.user)

    prev_start, prev_end = _prev_month(sel)
    prev_qs = Transaction.objects.filter(owner=request.user, occurred_on__gte=prev_start, occurred_on__lt=prev_end)

    total_expense = float(qs.filter(kind=Transaction.EXPENSE).aggregate(s=Sum("amount"))["s"] or Decimal("0"))
    total_income = float(qs.filter(kind=Transaction.INCOME).aggregate(s=Sum("amount"))["s"] or Decimal("0"))
    net = total_income - total_expense
    savings_rate = (net / total_income * 100) if total_income > 0 else 0.0
    gauge_pct = max(0.0, min(100.0, savings_rate))
    days_in_month = (end - start).days
    avg_daily = total_expense / days_in_month if days_in_month else 0.0
    tx_count = qs.count()
    today = date.today()
    is_current_cycle = sel.year == today.year and sel.month == today.month

    if is_current_cycle:
        pending = RecurringTransaction.objects.filter(
            owner=request.user,
            active=True,
            kind=RecurringTransaction.EXPENSE,
        ).exclude(
            Exists(Transaction.objects.filter(
                owner=request.user,
                recurring=OuterRef("pk"),
                occurred_on__gte=start,
                occurred_on__lt=end,
            ))
        ).select_related("bank", "category")
    else:
        pending = RecurringTransaction.objects.none()
    pending_count = pending.count()
    pending_total = float(sum((rule.amount for rule in pending), Decimal("0")))

    # Category movers: which categories changed most vs last month
    movers = _category_movers(qs, prev_qs)

    # Top spending days for the "top spending days" widget
    top_days = _top_spend_days(qs, start, end)
    largest_expenses = list(
        qs.filter(kind=Transaction.EXPENSE)
        .select_related("category", "bank")
        .order_by("-amount", "-occurred_on")[:6]
    )

    chart_data = {
        "trend": _trend(months, request.user),
        "evolution": _evolution(all_qs, months),
        "top": _top_cats(qs),
        "cat_comparison": _cat_comparison(qs, prev_qs),
        "burn_rate": _burn_rate(qs, all_qs),
        "weekly": _weekly_spend(qs, start, end),
        "movers": movers,
    }
    evo_count = len(chart_data["evolution"]["datasets"])

    return render(request, "analytics/_fragment.html", {
        "selected": sel,
        "month_options": month_options(),
        "total_expense": total_expense,
        "total_income": total_income,
        "net": net,
        "savings_rate": savings_rate,
        "gauge_pct": gauge_pct,
        "avg_daily": avg_daily,
        "tx_count": tx_count,
        "is_current_cycle": is_current_cycle,
        "pending": pending,
        "pending_count": pending_count,
        "pending_total": pending_total,
        "largest_expenses": largest_expenses,
        "top_days": top_days,
        "evo_count": evo_count,
        "chart_data_json": json.dumps(chart_data),
    })


def _prev_month(sel):
    y, m = sel.year, sel.month
    m -= 1
    if m == 0:
        m = 12
        y -= 1
    return month_bounds(date(y, m, 1))


def _trend(months, user):
    qs = Transaction.objects.filter(owner=user)
    rows = (
        qs.annotate(month=TruncMonth("occurred_on"))
        .values("month", "kind")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )
    bucket = defaultdict(lambda: {"income": 0.0, "expense": 0.0})
    for r in rows:
        bucket[_to_date(r["month"])][r["kind"]] = float(r["total"])
    return {
        "labels": [m.strftime("%b %y") for m in months],
        "income": [bucket[m]["income"] for m in months],
        "expense": [bucket[m]["expense"] for m in months],
    }


def _weekly_spend(qs, start, end):
    """Aggregate spending by week of the selected month."""
    from math import ceil
    days_in = (end - start).days
    weeks = ceil(days_in / 7)
    rows = (
        qs.filter(kind=Transaction.EXPENSE)
        .annotate(day=ExtractDay("occurred_on"))
        .values("day")
        .annotate(total=Sum("amount"))
    )
    daily = {r["day"]: float(r["total"]) for r in rows}
    labels, values = [], []
    for w in range(weeks):
        lo = w * 7 + 1
        hi = min((w + 1) * 7, days_in)
        week_total = sum(daily.get(d, 0.0) for d in range(lo, hi + 1))
        labels.append(f"Week {w + 1}")
        values.append(round(week_total, 2))
    return {"labels": labels, "values": values}


def _evolution(qs, months):
    top = list(
        qs.filter(kind=Transaction.EXPENSE)
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:TOP_CATS]
    )
    lookup = {r["category__name"]: r["category__color"] or DEFAULT_COLOR for r in top}
    rows = (
        qs.filter(kind=Transaction.EXPENSE)
        .annotate(month=TruncMonth("occurred_on"))
        .values("month", "category__name")
        .annotate(total=Sum("amount"))
    )
    series = {name: [0.0] * len(months) for name in lookup}
    for r in rows:
        name = r["category__name"]
        if name in series:
            try:
                series[name][months.index(_to_date(r["month"]))] = float(r["total"])
            except ValueError:
                pass
    return {
        "labels": [m.strftime("%b %y") for m in months],
        "datasets": [
            {"label": name, "color": lookup[name], "values": values}
            for name, values in series.items()
        ],
    }


def _top_cats(qs):
    rows = list(
        qs.filter(kind=Transaction.EXPENSE)
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:TOP_CATS]
    )
    return {
        "labels": [r["category__name"] or "Uncategorized" for r in rows],
        "values": [float(r["total"]) for r in rows],
        "colors": [r["category__color"] or DEFAULT_COLOR for r in rows],
    }


def _monthly_donut(qs):
    rows = list(
        qs.filter(kind=Transaction.EXPENSE)
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    return {
        "labels": [r["category__name"] or "Uncategorized" for r in rows],
        "values": [float(r["total"]) for r in rows],
        "colors": [r["category__color"] or DEFAULT_COLOR for r in rows],
    }


def _cat_comparison(qs, prev_qs):
    cur = {
        r["category__name"]: float(r["total"])
        for r in qs.filter(kind=Transaction.EXPENSE).values("category__name").annotate(total=Sum("amount"))
    }
    prev = {
        r["category__name"]: float(r["total"])
        for r in prev_qs.filter(kind=Transaction.EXPENSE).values("category__name").annotate(total=Sum("amount"))
    }
    all_cats = sorted(set(list(cur.keys()) + list(prev.keys())))
    return {
        "labels": all_cats,
        "this_month": [cur.get(c, 0.0) for c in all_cats],
        "last_month": [prev.get(c, 0.0) for c in all_cats],
    }


def _category_movers(qs, prev_qs):
    """Which categories changed most vs last month."""
    cur = {
        r["category__name"] or "Uncategorized": float(r["total"])
        for r in qs.filter(kind=Transaction.EXPENSE)
        .values("category__name")
        .annotate(total=Sum("amount"))
    }
    prev = {
        r["category__name"] or "Uncategorized": float(r["total"])
        for r in prev_qs.filter(kind=Transaction.EXPENSE)
        .values("category__name")
        .annotate(total=Sum("amount"))
    }
    deltas = []
    all_cats = set(list(cur.keys()) + list(prev.keys()))
    for name in all_cats:
        c = cur.get(name, 0.0)
        p = prev.get(name, 0.0)
        if c == 0 and p == 0:
            continue
        delta = c - p
        deltas.append({
            "label": name,
            "delta": delta,
            "current": c,
            "previous": p,
        })
    deltas.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return {
        "labels": [d["label"] for d in deltas[:8]],
        "deltas": [round(d["delta"], 2) for d in deltas[:8]],
        "values": [d["current"] for d in deltas[:8]],
    }


def _top_spend_days(qs, start, end):
    """Top 5-10 days with highest spending this month."""
    days = (end - start).days
    rows = (
        qs.filter(kind=Transaction.EXPENSE)
        .annotate(day=ExtractDay("occurred_on"))
        .values("day")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    max_amt = max((float(r["total"]) for r in rows), default=1)
    return [
        {"day": r["day"], "amount": float(r["total"]),
         "pct": round(float(r["total"]) / max_amt * 100, 1)}
        for r in rows[:10]
    ]
    prev = {
        r["category__name"] or "Uncategorized": float(r["total"])
        for r in prev_qs.filter(kind=Transaction.EXPENSE)
        .values("category__name")
        .annotate(total=Sum("amount"))
    }
    deltas = []
    all_cats = set(list(cur.keys()) + list(prev.keys()))
    for name in all_cats:
        c = cur.get(name, 0.0)
        p = prev.get(name, 0.0)
        if c == 0 and p == 0:
            continue
        delta = c - p
        deltas.append({
            "label": name,
            "delta": delta,
            "current": c,
            "previous": p,
        })
    deltas.sort(key=lambda x: abs(x["delta"]), reverse=True)
    return {
        "labels": [d["label"] for d in deltas[:8]],
        "deltas": [round(d["delta"], 2) for d in deltas[:8]],
        "values": [d["current"] for d in deltas[:8]],
    }


def _burn_rate(qs, all_qs):
    sample = qs.values_list("occurred_on", flat=True).first()
    if not sample:
        return {"labels": [], "cumulative": [], "projected": []}
    month_start, month_end = month_bounds(date(sample.year, sample.month, 1))
    days_in = (month_end - month_start).days

    rows = list(
        qs.filter(kind=Transaction.EXPENSE)
        .annotate(day=ExtractDay("occurred_on"))
        .values("day")
        .annotate(total=Sum("amount"))
        .order_by("day")
    )

    daily = {r["day"]: float(r["total"]) for r in rows}
    cumulative = []
    running = 0
    labels = []
    for d in range(1, days_in + 1):
        running += daily.get(d, 0.0)
        cumulative.append(running)
        labels.append(str(d))
    total = cumulative[-1] if cumulative else 0.0
    projected = [round(total / days_in * d, 2) for d in range(1, days_in + 1)]
    return {
        "labels": labels,
        "cumulative": cumulative,
        "projected": projected,
    }
