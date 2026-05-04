from datetime import date
from decimal import Decimal

from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from core.utils import month_bounds, month_options, selected_month
from transactions.models import Transaction

from .forms import RecurringForm
from .models import RecurringTransaction


def home(request):
    selected = selected_month(request.GET)
    start, end = month_bounds(selected)

    # is there a materialized tx for this rule in the selected month?
    done_sub = Transaction.objects.filter(
        recurring=OuterRef("pk"),
        occurred_on__gte=start,
        occurred_on__lt=end,
    )
    rules = (
        RecurringTransaction.objects
        .annotate(done=Exists(done_sub))
        .select_related("bank", "category")
    )

    active = rules.filter(active=True)
    to_pay = active.filter(kind=RecurringTransaction.EXPENSE, done=False).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    to_receive = active.filter(kind=RecurringTransaction.INCOME, done=False).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    paid_so_far = active.filter(kind=RecurringTransaction.EXPENSE, done=True).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    received_so_far = active.filter(kind=RecurringTransaction.INCOME, done=True).aggregate(s=Sum("amount"))["s"] or Decimal("0")

    return render(request, "recurring/list.html", {
        "rules": rules,
        "selected": selected,
        "month_options": month_options(),
        "to_pay": to_pay,
        "to_receive": to_receive,
        "paid_so_far": paid_so_far,
        "received_so_far": received_so_far,
        "net_remaining": to_receive - to_pay,
    })


@require_http_methods(["GET", "POST"])
def create(request):
    if request.method == "POST":
        form = RecurringForm(request.POST)
        if form.is_valid():
            form.save()
            return _refresh()
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
            return _refresh()
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
        return _refresh()
    return render(request, "recurring/_delete_modal.html", {
        "rule": rule,
        "submit_url": request.path,
    })


@require_http_methods(["POST"])
def toggle_done(request, pk):
    rule = get_object_or_404(RecurringTransaction, pk=pk)
    month = selected_month(request.POST)
    start, end = month_bounds(month)

    existing = Transaction.objects.filter(
        recurring=rule,
        occurred_on__gte=start, occurred_on__lt=end,
    ).first()

    if existing:
        existing.delete()
    else:
        # if marking the current month, use today (real moment of payment).
        # otherwise fall back to the scheduled day_of_month for that cycle.
        today = date.today()
        if start <= today < end:
            target = today
        else:
            target = date(month.year, month.month, rule.day_of_month)

        Transaction.objects.create(
            name=rule.name,
            kind=rule.kind,
            amount=rule.amount,
            bank=rule.bank,
            category=rule.category,
            occurred_on=target,
            notes=rule.notes,
            recurring=rule,
        )
        if not rule.last_materialized_on or rule.last_materialized_on < target:
            rule.last_materialized_on = target
            rule.save(update_fields=["last_materialized_on"])

    return _refresh()


def _refresh():
    response = HttpResponse(status=204)
    response["HX-Refresh"] = "true"
    return response
