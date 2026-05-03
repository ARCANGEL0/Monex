from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .forms import TransactionForm
from .models import Transaction


def _parse_month(s):
    # accepts YYYY-MM, returns first-of-month
    try:
        y, m = s.split("-")
        return date(int(y), int(m), 1)
    except (ValueError, AttributeError, TypeError):
        return None


def _month_bounds(d):
    if d.month == 12:
        nxt = date(d.year + 1, 1, 1)
    else:
        nxt = date(d.year, d.month + 1, 1)
    return d, nxt


def _month_options(months_back=24):
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


def transaction_list(request):
    today = date.today()
    selected = _parse_month(request.GET.get("month")) or date(today.year, today.month, 1)
    start, end = _month_bounds(selected)

    qs = (
        Transaction.objects
        .filter(occurred_on__gte=start, occurred_on__lt=end)
        .select_related("bank", "category")
        .order_by("-occurred_on", "-id")
    )

    income_total = qs.filter(kind=Transaction.INCOME).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    expense_total = qs.filter(kind=Transaction.EXPENSE).aggregate(s=Sum("amount"))["s"] or Decimal("0")

    return render(request, "transactions/list.html", {
        "transactions": qs,
        "selected": selected,
        "month_options": _month_options(),
        "income_total": income_total,
        "expense_total": expense_total,
        "net": income_total - expense_total,
    })


@require_http_methods(["GET", "POST"])
def transaction_create(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            # tells htmx to reload the page so kpis + table update
            response = HttpResponse(status=204)
            response["HX-Refresh"] = "true"
            return response
    else:
        form = TransactionForm(initial={
            "kind": Transaction.EXPENSE,
            "occurred_on": date.today(),
        })

    return render(request, "transactions/_form_modal.html", {
        "form": form,
        "title": "log entry",
        "submit_url": request.path,
        "submit_label": "Log Entry",
    })


@require_http_methods(["GET", "POST"])
def transaction_edit(request, pk):
    t = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        form = TransactionForm(request.POST, instance=t)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Refresh"] = "true"
            return response
    else:
        form = TransactionForm(instance=t)

    return render(request, "transactions/_form_modal.html", {
        "form": form,
        "title": "edit entry",
        "submit_url": request.path,
        "submit_label": "Update",
    })


@require_http_methods(["GET", "POST"])
def transaction_delete(request, pk):
    t = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        t.delete()
        response = HttpResponse(status=204)
        response["HX-Refresh"] = "true"
        return response

    return render(request, "transactions/_delete_modal.html", {
        "transaction": t,
        "submit_url": request.path,
    })
