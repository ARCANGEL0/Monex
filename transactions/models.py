from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Bank(models.Model):
    name = models.CharField(max_length=80, unique=True)
    color = models.CharField(max_length=7, default="#c9a227")
    icon = models.CharField(max_length=40, blank=True)
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(models.Model):
    INCOME = "income"
    EXPENSE = "expense"
    KIND_CHOICES = [(INCOME, "income"), (EXPENSE, "expense")]

    name = models.CharField(max_length=80, unique=True)
    color = models.CharField(max_length=7, default="#c9a227")
    icon = models.CharField(max_length=40, blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=EXPENSE)
    archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name


class Transaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"
    KIND_CHOICES = [(INCOME, "income"), (EXPENSE, "expense")]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="transactions", null=True,
    )
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    occurred_on = models.DateField(default=date.today)
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, related_name="transactions")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, blank=True,
        related_name="transactions",
    )
    notes = models.TextField(blank=True)
    recurring = models.ForeignKey(
        "recurring.RecurringTransaction", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="instances",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-occurred_on", "-id"]
        indexes = [
            models.Index(fields=["occurred_on"]),
            models.Index(fields=["kind", "occurred_on"]),
        ]

    def __str__(self):
        return f"{self.name} {self.amount}"

    @property
    def signed_amount(self):
        return -self.amount if self.kind == self.EXPENSE else self.amount


class Budget(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="budgets", null=True,
    )
    month = models.DateField()
    overall_cap = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        unique_together = ("owner", "month")
        ordering = ["-month"]

    def __str__(self):
        return f"budget {self.owner.username} {self.month:%Y-%m}"


class CategoryBudget(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="category_budgets", null=True,
    )
    month = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
    cap = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        unique_together = ("owner", "month", "category")
        ordering = ["-month", "category__name"]

    def __str__(self):
        return f"{self.owner.username} / {self.category.name} {self.cap} ({self.month:%Y-%m})"
