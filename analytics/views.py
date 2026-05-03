from collections import defaultdict
from datetime import date

from django.db.models import Sum
from django.db.models.functions import ExtractIsoWeekDay, TruncMonth
from django.shortcuts import render

from transactions.models import Transaction


TREND_MONTHS = 12
TOP_CATS = 6
TOP_ALL = 10
DEFAULT_COLOR = "#7a7466"


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
    months = _months_range()
    start = months[0]

    qs = Transaction.objects.filter(occurred_on__gte=start)

    return render(request, "analytics/home.html", {
        "chart_data": {
            "trend": _trend(qs, months),
            "dow": _dow(),
            "evolution": _evolution(qs, months),
            "top": _top_all(),
        },
    })


def _trend(qs, months):
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


def _dow():
    rows = (
        Transaction.objects.filter(kind=Transaction.EXPENSE)
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
    # top N categories all-time, then evolution for those over the last N months
    top = list(
        Transaction.objects.filter(kind=Transaction.EXPENSE)
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


def _top_all():
    rows = list(
        Transaction.objects.filter(kind=Transaction.EXPENSE)
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:TOP_ALL]
    )
    return {
        "labels": [r["category__name"] or "Uncategorized" for r in rows],
        "values": [float(r["total"]) for r in rows],
        "colors": [r["category__color"] or DEFAULT_COLOR for r in rows],
    }
