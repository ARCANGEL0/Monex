from django.core.management.base import BaseCommand

from transactions.models import Bank, Category


# kept on-palette - amber/bronze/olive/red. no rainbow.
BANKS = [
    ("Revolut", "#c9a227"),
    ("N26", "#d97706"),
    ("Wise", "#92400e"),
    ("ING", "#b45309"),
    ("Cash", "#7a9a47"),
]

INCOME_CATEGORIES = [
    ("Salary", "#7a9a47"),
    ("Freelance", "#65803a"),
    ("Investment", "#ca8a04"),
    ("Other Income", "#a16207"),
]

EXPENSE_CATEGORIES = [
    ("Groceries", "#c9a227"),
    ("Rent", "#92400e"),
    ("Utilities", "#d97706"),
    ("Transport", "#f59e0b"),
    ("Dining", "#ea580c"),
    ("Entertainment", "#b45309"),
    ("Health", "#b91c1c"),
    ("Shopping", "#fcd34d"),
    ("Subscriptions", "#78350f"),
    ("Travel", "#e8b923"),
    ("Other", "#7a7466"),
]


class Command(BaseCommand):
    help = "seed default banks and categories. safe to re-run."

    def handle(self, *args, **opts):
        for name, color in BANKS:
            _, created = Bank.objects.get_or_create(name=name, defaults={"color": color})
            if created:
                self.stdout.write(f"+ bank {name}")

        for name, color in INCOME_CATEGORIES:
            _, created = Category.objects.get_or_create(
                name=name,
                defaults={"color": color, "kind": Category.INCOME},
            )
            if created:
                self.stdout.write(f"+ income/{name}")

        for name, color in EXPENSE_CATEGORIES:
            _, created = Category.objects.get_or_create(
                name=name,
                defaults={"color": color, "kind": Category.EXPENSE},
            )
            if created:
                self.stdout.write(f"+ expense/{name}")

        self.stdout.write(self.style.SUCCESS("seed complete"))
