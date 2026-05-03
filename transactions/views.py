from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from core.utils import month_bounds, month_options, selected_month

from .forms import TransactionForm
from .models import Transaction


def transaction_list(request):
    selected = selected_month(request.GET)
    start, end = month_bounds(selected)

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
        "month_options": month_options(),
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
