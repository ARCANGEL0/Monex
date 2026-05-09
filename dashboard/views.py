import json
from decimal import Decimal

from django.db.models import Exists, OuterRef, Sum
from django.shortcuts import redirect, render

from core.utils import month_bounds, month_options, selected_month
from transactions.models import Budget, Transaction
from recurring.models import RecurringTransaction

CATEGORY_DONUT_TOP = 7
OTHER_COLOR = "#7a7466"


def _htmx(request):
    return bool(request.headers.get("HX-Request"))


def home(request):
    if not _htmx(request):
        return redirect("core:root")
    selected = selected_month(request.GET)
    start, end = month_bounds(selected)

    qs = Transaction.objects.filter(
        owner=request.user,
        occurred_on__gte=start, occurred_on__lt=end,
    )

    income = qs.filter(kind=Transaction.INCOME).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    expense = qs.filter(kind=Transaction.EXPENSE).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    net = income - expense
    savings_rate = (net / income * 100) if income > 0 else Decimal("0")
    gauge_pct = max(0.0, min(100.0, float(savings_rate)))
    tx_count = qs.count()
    chart_data = {
        "by_category": _by_category(qs),
        "by_bank": _by_bank(qs),
    }

    # Pending recurring expenses for this cycle
    from datetime import date
    today = date.today()
    if selected.year == today.year and selected.month == today.month:
        from core.utils import month_bounds as mb
        ms, me = month_bounds(selected)
        pending = RecurringTransaction.objects.filter(
            owner=request.user,
            active=True,
            kind=RecurringTransaction.EXPENSE,
        ).exclude(
            Exists(Transaction.objects.filter(
                owner=request.user,
                recurring=OuterRef("pk"),
                occurred_on__gte=ms,
                occurred_on__lt=me,
            ))
        ).select_related("bank", "category")
    else:
        pending = RecurringTransaction.objects.none()
    pending_count = pending.count()
    pending_total = sum((rule.amount for rule in pending), Decimal("0"))

    # Recent transactions
    recent = qs.select_related("category", "bank").order_by("-occurred_on", "-created_at")[:7]

    # Period progress
    from datetime import date as d
    today = d.today()
    if selected.year == today.year and selected.month == today.month:
        days_in = (end - start).days
        day_of = (today - start).days + 1
        period_progress = day_of / days_in * 100
    else:
        period_progress = None

    # Biggest expense this cycle
    biggest = qs.filter(kind=Transaction.EXPENSE).order_by("-amount").select_related("category", "bank").first()

    return render(request, "dashboard/_fragment.html", {
        "selected": selected,
        "month_options": month_options(),
        "income": income,
        "expense": expense,
        "net": net,
        "savings_rate": savings_rate,
        "gauge_pct": gauge_pct,
        "tx_count": tx_count,
        "chart_data_json": json.dumps(chart_data),
        "budget": _budget_status(request.user, selected, expense),
        "pending": pending,
        "pending_count": pending_count,
        "pending_total": pending_total,
        "recent": recent,
        "period_progress": period_progress,
        "biggest": biggest,
    })


def _budget_status(user, month, expense):
    b = Budget.objects.filter(owner=user, month=month).first()
    if not b or not b.overall_cap:
        return None
    cap = b.overall_cap
    pct = float(expense / cap * 100) if cap > 0 else 0
    return {
        "cap": cap,
        "spent": expense,
        "pct": pct,
        "bar_width": min(100.0, pct),
        "remaining": max(Decimal("0"), cap - expense),
        "over": pct >= 100,
        "warn": 80 <= pct < 100,
    }


def _by_category(qs):
    rows = list(
        qs.filter(kind=Transaction.EXPENSE)
        .values("category__name", "category__color")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )
    top = rows[:CATEGORY_DONUT_TOP]
    rest = rows[CATEGORY_DONUT_TOP:]
    out = [
        {
            "label": r["category__name"] or "Uncategorized",
            "color": r["category__color"] or OTHER_COLOR,
            "value": float(r["total"]),
        }
        for r in top
    ]
    if rest:
        out.append({
            "label": "Other",
            "color": OTHER_COLOR,
            "value": float(sum(r["total"] for r in rest)),
        })
    return out


def _by_bank(qs):
    rows = (
        qs.values("bank__name", "bank__color", "kind")
        .annotate(total=Sum("amount"))
        .order_by("bank__name")
    )
    banks = {}
    for r in rows:
        name = r["bank__name"]
        if name not in banks:
            banks[name] = {"label": name, "color": r["bank__color"] or "#c9a227", "income": 0.0, "expense": 0.0}
        banks[name][r["kind"]] = float(r["total"])
    return list(banks.values())
