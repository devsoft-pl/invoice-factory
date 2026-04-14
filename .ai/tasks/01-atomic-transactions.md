# Task 01: Wrap multi-step operations in atomic transactions

## Priority: CRITICAL
## Status: done
## Estimated scope: small

## Problem

Invoice duplication and batch operations are not wrapped in database transactions. If a save fails halfway through, the database is left in an inconsistent state.

## Files to modify

- `invoices/views.py` — `duplicate_company_invoice_view`, `duplicate_individual_invoice_view`
- `invoices/tasks.py` — `send_monthly_summary_to_recipients`
- `invoices/utils.py` — verify `create_recurrent_invoices`

## Steps

1. Read `invoices/views.py` — find `duplicate_company_invoice_view` and `duplicate_individual_invoice_view`
2. Wrap the entire creation block (save Invoice + loop save Items) in `with transaction.atomic():`
3. Read `invoices/tasks.py` — find `send_monthly_summary_to_recipients`
4. Replace the loop `for invoice in invoices: invoice.is_settled = True; invoice.save()` with:
   ```python
   with transaction.atomic():
       invoices.update(is_settled=True)
   ```
5. Read `invoices/utils.py` — check `create_recurrent_invoices`; if it creates multiple objects, wrap in a transaction too
6. Import: `from django.db import transaction`
7. Run `pytest invoices/` — ensure tests pass

## Acceptance criteria

- Invoice duplication is atomic — either the full invoice with items is created, or nothing
- Setting `is_settled` is atomic
- Existing tests pass
- Optional: new test asserting that a mid-transaction failure leaves no partial data

## References

- Django docs: https://docs.djangoproject.com/en/5.2/topics/db/transactions/
