import json
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_not_required
from django.db.models import Exists, OuterRef, Sum
from django.shortcuts import redirect, render

from core.utils import month_bounds, month_options, selected_month
from recurring.models import RecurringTransaction
from transactions.models import Budget, Transaction

CATEGORY_DONUT_TOP = 7
OTHER_COLOR = "#7a7466"
User = get_user_model()


@login_not_required
def root(request):
    if not request.user.is_authenticated:
        if not User.objects.filter(is_superuser=True).exists():
            return redirect("accounts:first_run")
        return redirect("accounts:login")
    return render(request, "core/shell.html", _dashboard_ctx(request))


def _dashboard_ctx(request):
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
    today = date.today()
    if selected.year == today.year and selected.month == today.month:
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
    pending_total = sum((rule.amount for rule in pending), Decimal("0"))

    chart_data = {
        "by_category": _by_category(qs),
        "by_bank": _by_bank(qs),
    }

    return {
        "selected": selected,
        "month_options": month_options(),
        "income": income,
        "expense": expense,
        "net": net,
        "savings_rate": savings_rate,
        "gauge_pct": gauge_pct,
        "tx_count": tx_count,
        "pending": pending,
        "pending_count": pending_count,
        "pending_total": pending_total,
        "chart_data_json": json.dumps(chart_data),
        "budget": _budget_status(request.user, selected, expense),
    }


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
