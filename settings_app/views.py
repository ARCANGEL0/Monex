from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.utils import month_options, selected_month
from transactions.models import Bank, Budget, Category, CategoryBudget

from .forms import BankForm, CategoryForm


def home(request):
    selected = selected_month(request.GET)
    tab = request.GET.get("tab", "budget")

    budget = Budget.objects.filter(month=selected).first()
    cat_caps = {cb.category_id: cb.cap for cb in CategoryBudget.objects.filter(month=selected)}
    expense_cats = list(Category.objects.filter(archived=False, kind=Category.EXPENSE).order_by("name"))
    cat_rows = [(c, cat_caps.get(c.pk)) for c in expense_cats]

    banks = Bank.objects.all()
    categories = Category.objects.all()

    return render(request, "settings/home.html", {
        "tab": tab,
        "selected": selected,
        "month_options": month_options(),
        "budget": budget,
        "cat_rows": cat_rows,
        "banks": banks,
        "categories": categories,
    })


@require_http_methods(["POST"])
def budget_save(request):
    selected = selected_month(request.POST)

    overall_raw = (request.POST.get("overall_cap") or "").strip()
    overall_cap = _parse_decimal(overall_raw)

    budget, _ = Budget.objects.get_or_create(month=selected)
    budget.overall_cap = overall_cap
    budget.save()

    # per-category
    for cat in Category.objects.filter(archived=False, kind=Category.EXPENSE):
        raw = (request.POST.get(f"cap_{cat.pk}") or "").strip()
        cap = _parse_decimal(raw)
        if cap is None or cap <= 0:
            CategoryBudget.objects.filter(month=selected, category=cat).delete()
        else:
            CategoryBudget.objects.update_or_create(
                month=selected, category=cat, defaults={"cap": cap},
            )

    messages.success(request, "budget updated.")
    return redirect(f"/settings/?tab=budget&month={selected:%Y-%m}")


def _parse_decimal(raw):
    if not raw:
        return None
    try:
        return Decimal(raw)
    except (InvalidOperation, TypeError):
        return None


# banks ---------------------------------------------------------------

@require_http_methods(["GET", "POST"])
def bank_create(request):
    if request.method == "POST":
        form = BankForm(request.POST)
        if form.is_valid():
            form.save()
            return _refresh()
    else:
        form = BankForm(initial={"color": "#c9a227"})
    return render(request, "settings/_bank_form.html", {
        "form": form, "title": "new bank", "submit_url": request.path, "submit_label": "Create",
    })


@require_http_methods(["GET", "POST"])
def bank_edit(request, pk):
    bank = get_object_or_404(Bank, pk=pk)
    if request.method == "POST":
        form = BankForm(request.POST, instance=bank)
        if form.is_valid():
            form.save()
            return _refresh()
    else:
        form = BankForm(instance=bank)
    return render(request, "settings/_bank_form.html", {
        "form": form, "title": "edit bank", "submit_url": request.path, "submit_label": "Update",
    })


@require_http_methods(["GET", "POST"])
def bank_delete(request, pk):
    bank = get_object_or_404(Bank, pk=pk)
    if request.method == "POST":
        try:
            bank.delete()
            return _refresh()
        except ProtectedError:
            return render(request, "settings/_delete_modal.html", {
                "subject": bank.name,
                "submit_url": request.path,
                "error": "this bank has linked transactions. archive it instead.",
                "title": "delete bank",
            })
    return render(request, "settings/_delete_modal.html", {
        "subject": bank.name, "submit_url": request.path, "title": "delete bank",
    })


# categories ----------------------------------------------------------

@require_http_methods(["GET", "POST"])
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return _refresh()
    else:
        form = CategoryForm(initial={"color": "#c9a227", "kind": Category.EXPENSE})
    return render(request, "settings/_cat_form.html", {
        "form": form, "title": "new category", "submit_url": request.path, "submit_label": "Create",
    })


@require_http_methods(["GET", "POST"])
def category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        form = CategoryForm(request.POST, instance=cat)
        if form.is_valid():
            form.save()
            return _refresh()
    else:
        form = CategoryForm(instance=cat)
    return render(request, "settings/_cat_form.html", {
        "form": form, "title": "edit category", "submit_url": request.path, "submit_label": "Update",
    })


@require_http_methods(["GET", "POST"])
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == "POST":
        try:
            cat.delete()
            return _refresh()
        except ProtectedError:
            return render(request, "settings/_delete_modal.html", {
                "subject": cat.name,
                "submit_url": request.path,
                "error": "this category has linked transactions. archive it instead.",
                "title": "delete category",
            })
    return render(request, "settings/_delete_modal.html", {
        "subject": cat.name, "submit_url": request.path, "title": "delete category",
    })


def _refresh():
    response = HttpResponse(status=204)
    response["HX-Refresh"] = "true"
    return response
