# Task 04: Fix N+1 invoice saves triggered by Item.save()

## Priority: HIGH
## Status: todo
## Estimated scope: medium

## Problem

`Item.save()` and `Item.delete()` recalculate and save the parent Invoice. Adding 10 items fires 10 UPDATE queries on Invoice. Duplicating an invoice with N items results in N+1 saves instead of one.

## Files to modify

- `items/models.py` — remove auto-save of Invoice from `save()` / `delete()`
- `invoices/models.py` — add `recalculate_totals()` method
- `invoices/views.py` — call `recalculate_totals()` after item operations
- `invoices/utils.py` — verify `create_recurrent_invoices`
- `items/views.py` — call `recalculate_totals()` after item CRUD
- `items/tests/` — update tests

## Steps

1. Read `items/models.py` — analyse existing `save()` and `delete()`
2. Read `invoices/models.py` — review `calculate_net_amount()` and `calculate_gross_amount()`
3. Add a method to `Invoice`:
   ```python
   def recalculate_totals(self):
       self.net_amount = self.calculate_net_amount()
       self.gross_amount = self.calculate_gross_amount()
       self.save(update_fields=["net_amount", "gross_amount"])
   ```
4. In `Item.save()` — remove automatic Invoice recalculation (keep only `super().save()`)
5. In `Item.delete()` — remove automatic Invoice recalculation (keep only `super().delete()`)
6. Find ALL places that create / edit / delete Items — add `invoice.recalculate_totals()` after the operation completes
7. Search in: `items/views.py`, `invoices/views.py`, `invoices/utils.py`, `invoices/tasks.py`
8. Run `pytest .` — fix tests that relied on auto-recalculation

## Constraints

- Do not change the calculation logic (net_amount, tax_amount, gross_amount) — only the point at which it is triggered
- `recalculate_totals()` must be called ONCE after batch operations, not after each individual item

## Acceptance criteria

- `Item.save()` does not call `Invoice.save()`
- `Item.delete()` does not call `Invoice.save()`
- New method `Invoice.recalculate_totals()` exists and is used everywhere
- Duplicating an invoice with N items produces 1 Invoice save (not N+1)
- All tests pass
- Invoice amounts remain correct
