from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .forms import RecurringForm
from .models import RecurringTransaction


def home(request):
    rules = RecurringTransaction.objects.select_related("bank", "category").all()

    income_monthly = rules.filter(active=True, kind=RecurringTransaction.INCOME).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    expense_monthly = rules.filter(active=True, kind=RecurringTransaction.EXPENSE).aggregate(s=Sum("amount"))["s"] or Decimal("0")

    return render(request, "recurring/list.html", {
        "rules": rules,
        "income_monthly": income_monthly,
        "expense_monthly": expense_monthly,
        "net_monthly": income_monthly - expense_monthly,
    })


@require_http_methods(["GET", "POST"])
def create(request):
    if request.method == "POST":
        form = RecurringForm(request.POST)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Refresh"] = "true"
            return response
    else:
        form = RecurringForm(initial={"kind": RecurringTransaction.EXPENSE, "active": True, "day_of_month": 1})

    return render(request, "recurring/_form_modal.html", {
        "form": form,
        "title": "new recurring rule",
        "submit_url": request.path,
        "submit_label": "Create",
    })


@require_http_methods(["GET", "POST"])
def edit(request, pk):
    rule = get_object_or_404(RecurringTransaction, pk=pk)
    if request.method == "POST":
        form = RecurringForm(request.POST, instance=rule)
        if form.is_valid():
            form.save()
            response = HttpResponse(status=204)
            response["HX-Refresh"] = "true"
            return response
    else:
        form = RecurringForm(instance=rule)

    return render(request, "recurring/_form_modal.html", {
        "form": form,
        "title": "edit recurring rule",
        "submit_url": request.path,
        "submit_label": "Update",
    })


@require_http_methods(["GET", "POST"])
def delete(request, pk):
    rule = get_object_or_404(RecurringTransaction, pk=pk)
    if request.method == "POST":
        rule.delete()
        response = HttpResponse(status=204)
        response["HX-Refresh"] = "true"
        return response
    return render(request, "recurring/_delete_modal.html", {
        "rule": rule,
        "submit_url": request.path,
    })
