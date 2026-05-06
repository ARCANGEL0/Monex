import json
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import ExtractIsoWeekDay, ExtractDay, TruncMonth
from django.shortcuts import redirect, render

from core.utils import month_bounds, month_options, selected_month
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
    days_in_month = (end - start).days
    avg_daily = total_expense / days_in_month if days_in_month else 0.0
    tx_count = qs.count()

    chart_data = {
        "trend": _trend(months),
        "dow": _dow(request.user),
        "evolution": _evolution(all_qs, months),
        "top": _top_cats(qs),
        "monthly_donut": _monthly_donut(qs),
        "cat_comparison": _cat_comparison(qs, prev_qs),
        "daily_bars": _daily_bars(qs, start, end),
        "burn_rate": _burn_rate(qs, all_qs),
    }
    evo_count = len(chart_data["evolution"]["datasets"])

    return render(request, "analytics/_fragment.html", {
        "selected": sel,
        "month_options": month_options(),
        "total_expense": total_expense,
        "total_income": total_income,
        "avg_daily": avg_daily,
        "tx_count": tx_count,
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


def _trend(months):
    qs = Transaction.objects.all()
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


def _dow(user):
    rows = (
        Transaction.objects.filter(owner=user, kind=Transaction.EXPENSE)
        .annotate(dow=ExtractIsoWeekDay("occurred_on"))
        .values("dow")
        .annotate(total=Sum("amount"))
        .order_by("dow")
    )
    by_day = {r["dow"]: float(r["total"]) for r in rows}
    return {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "values": [by_day.get(i, 0.0) for i in range(1, 8)],
    }


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


def _daily_bars(qs, start, end):
    days = (end - start).days
    rows = {
        r["day"]: float(r["total"])
        for r in qs.filter(kind=Transaction.EXPENSE)
        .annotate(day=ExtractDay("occurred_on"))
        .values("day")
        .annotate(total=Sum("amount"))
    }
    return {
        "labels": [str(d) for d in range(1, days + 1)],
        "values": [rows.get(d, 0.0) for d in range(1, days + 1)],
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
