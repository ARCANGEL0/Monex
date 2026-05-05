from decimal import Decimal, InvalidOperation
from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from core.context_processors import CURRENCIES
from core.utils import month_options, selected_month
from transactions.models import Bank, Budget, Category, CategoryBudget

from .forms import BankForm, CategoryForm, OperatorForm

User = get_user_model()


def _htmx(request):
    return bool(request.headers.get("HX-Request"))


def currency_save(request):
    code = request.POST.get("currency_code", "EUR").strip().upper()
    sym = CURRENCIES.get(code, "€")
    request.session["currency"] = sym
    request.session["currency_code"] = code
    back = request.POST.get("back", "/_/s/?tab=budget")
    return redirect(back)


def superuser_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return HttpResponseForbidden("superadmin only")
        return view(request, *args, **kwargs)
    return wrapped


def home(request):
    if not _htmx(request):
        return redirect("core:root")
    selected = selected_month(request.GET)
    tab = request.GET.get("tab", "budget")

    budget = Budget.objects.filter(owner=request.user, month=selected).first()
    cat_caps = {
        cb.category_id: cb.cap
        for cb in CategoryBudget.objects.filter(owner=request.user, month=selected)
    }
    expense_cats = list(Category.objects.filter(archived=False, kind=Category.EXPENSE).order_by("name"))
    cat_rows = [(c, cat_caps.get(c.pk)) for c in expense_cats]

    banks = Bank.objects.all()
    categories = Category.objects.all()
    users = User.objects.order_by("username") if request.user.is_superuser else User.objects.none()

    return render(request, "settings/_fragment.html", {
        "tab": tab,
        "selected": selected,
        "month_options": month_options(),
        "budget": budget,
        "cat_rows": cat_rows,
        "banks": banks,
        "categories": categories,
        "users": users,
    })


@require_http_methods(["POST"])
def budget_save(request):
    if not _htmx(request):
        return redirect("core:root")
    selected = selected_month(request.POST)

    overall_raw = (request.POST.get("overall_cap") or "").strip()
    overall_cap = _parse_decimal(overall_raw)

    budget, _ = Budget.objects.get_or_create(owner=request.user, month=selected)
    budget.overall_cap = overall_cap
    budget.save()

    for cat in Category.objects.filter(archived=False, kind=Category.EXPENSE):
        raw = (request.POST.get(f"cap_{cat.pk}") or "").strip()
        cap = _parse_decimal(raw)
        if cap is None or cap <= 0:
            CategoryBudget.objects.filter(owner=request.user, month=selected, category=cat).delete()
        else:
            CategoryBudget.objects.update_or_create(
                owner=request.user, month=selected, category=cat, defaults={"cap": cap},
            )

    messages.success(request, "budget updated.")
    return redirect(f"/_/s/?tab=budget&month={selected:%Y-%m}")


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
    if not _htmx(request):
        return redirect("core:root")
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
    if not _htmx(request):
        return redirect("core:root")
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
    if not _htmx(request):
        return redirect("core:root")
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
    if not _htmx(request):
        return redirect("core:root")
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
    if not _htmx(request):
        return redirect("core:root")
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
    if not _htmx(request):
        return redirect("core:root")
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


# users (superadmin only) ---------------------------------------------

@superuser_required
@require_http_methods(["GET", "POST"])
def user_create(request):
    if not _htmx(request):
        return redirect("core:root")
    if request.method == "POST":
        form = OperatorForm(request.POST, creating=True)
        if form.is_valid():
            form.save()
            return _refresh()
    else:
        form = OperatorForm(creating=True)
    return render(request, "settings/_user_form.html", {
        "form": form, "title": "new operator",
        "submit_url": request.path, "submit_label": "Create",
    })


@superuser_required
@require_http_methods(["GET", "POST"])
def user_edit(request, pk):
    if not _htmx(request):
        return redirect("core:root")
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = OperatorForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return _refresh()
    else:
        form = OperatorForm(instance=user)
    return render(request, "settings/_user_form.html", {
        "form": form, "title": "edit operator",
        "submit_url": request.path, "submit_label": "Update",
    })


@superuser_required
@require_http_methods(["GET", "POST"])
def user_delete(request, pk):
    if not _htmx(request):
        return redirect("core:root")
    user = get_object_or_404(User, pk=pk)
    if user.pk == request.user.pk:
        return render(request, "settings/_delete_modal.html", {
            "subject": user.username,
            "submit_url": request.path,
            "error": "you can't delete your own account.",
            "title": "delete operator",
        })
    if request.method == "POST":
        user.delete()
        return _refresh()
    return render(request, "settings/_delete_modal.html", {
        "subject": user.username,
        "submit_url": request.path,
        "title": "delete operator",
    })
