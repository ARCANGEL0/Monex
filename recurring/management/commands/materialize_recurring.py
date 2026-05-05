from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction as db_tx

from recurring.models import RecurringTransaction
from transactions.models import Transaction


class Command(BaseCommand):
    help = "materialize active recurring rules whose day_of_month has arrived this cycle. idempotent."

    def handle(self, *args, **opts):
        today = date.today()
        rules = RecurringTransaction.objects.filter(active=True).select_related("bank", "category")
        created = 0

        for rule in rules:
            target = date(today.year, today.month, rule.day_of_month)
            # not yet due this month
            if target > today:
                continue
            # already done for this cycle
            if rule.last_materialized_on and rule.last_materialized_on >= target:
                continue

            with db_tx.atomic():
                Transaction.objects.create(
                    owner=rule.owner,
                    name=rule.name,
                    kind=rule.kind,
                    amount=rule.amount,
                    bank=rule.bank,
                    category=rule.category,
                    occurred_on=target,
                    notes=rule.notes,
                    recurring=rule,
                )
                rule.last_materialized_on = target
                rule.save(update_fields=["last_materialized_on"])
            created += 1

        self.stdout.write(self.style.SUCCESS(f"materialized {created} entr{'y' if created == 1 else 'ies'}"))
