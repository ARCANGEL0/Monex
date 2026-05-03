from datetime import date
from decimal import Decimal

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

    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    # always positive - kind tells us direction
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
        # for display - negative on expenses
        return -self.amount if self.kind == self.EXPENSE else self.amount


class Budget(models.Model):
    # one row per month for the overall cap
    month = models.DateField(unique=True)
    overall_cap = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        ordering = ["-month"]

    def __str__(self):
        return f"budget {self.month:%Y-%m}"


class CategoryBudget(models.Model):
    month = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
    cap = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    class Meta:
        unique_together = ("month", "category")
        ordering = ["-month", "category__name"]

    def __str__(self):
        return f"{self.category.name} {self.cap} ({self.month:%Y-%m})"
