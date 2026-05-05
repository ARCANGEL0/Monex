from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class RecurringTransaction(models.Model):
    INCOME = "income"
    EXPENSE = "expense"
    KIND_CHOICES = [(INCOME, "income"), (EXPENSE, "expense")]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="recurring_rules", null=True,
    )
    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES)
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    bank = models.ForeignKey(
        "transactions.Bank", on_delete=models.PROTECT,
        related_name="recurring_rules",
    )
    category = models.ForeignKey(
        "transactions.Category", on_delete=models.PROTECT,
        null=True, blank=True, related_name="recurring_rules",
    )
    # 1-28 to dodge month-end edge cases (no feb 30)
    day_of_month = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(28)],
    )
    active = models.BooleanField(default=True)
    last_materialized_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["day_of_month", "name"]

    def __str__(self):
        return f"{self.name} (day {self.day_of_month})"

    @property
    def next_run(self):
        today = date.today()
        target = date(today.year, today.month, self.day_of_month)
        if target <= today:
            # already passed this month, push to next
            if today.month == 12:
                return date(today.year + 1, 1, self.day_of_month)
            return date(today.year, today.month + 1, self.day_of_month)
        return target
