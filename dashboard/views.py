from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render

from core.utils import month_bounds, month_options, selected_month
from transactions.models import Transaction


def home(request):
    selected = selected_month(request.GET)
    start, end = month_bounds(selected)

    qs = Transaction.objects.filter(occurred_on__gte=start, occurred_on__lt=end)

    income = qs.filter(kind=Transaction.INCOME).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    expense = qs.filter(kind=Transaction.EXPENSE).aggregate(s=Sum("amount"))["s"] or Decimal("0")
    net = income - expense
    savings_rate = (net / income * 100) if income > 0 else Decimal("0")

    return render(request, "dashboard/home.html", {
        "selected": selected,
        "month_options": month_options(),
        "income": income,
        "expense": expense,
        "net": net,
        "savings_rate": savings_rate,
    })
