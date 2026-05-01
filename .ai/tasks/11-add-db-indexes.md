# Task 11: Add database indexes on frequently filtered fields

## Priority: LOW
## Status: todo
## Estimated scope: small

## Problem

Fields `sale_date`, `create_date`, `is_recurring`, and `is_settled` are used frequently in queryset filters but have no indexes, causing full table scans as data grows.

## Files to modify

- `invoices/models.py` — Invoice model

## Steps

1. Read `invoices/models.py`
2. Add composite indexes in `Meta`:
   ```python
   class Meta:
       indexes = [
           models.Index(fields=["sale_date"], name="invoice_sale_date_idx"),
           models.Index(fields=["create_date"], name="invoice_create_date_idx"),
           models.Index(fields=["is_recurring", "is_last_day"], name="invoice_recurring_idx"),
       ]
   ```
3. Run `make makemigrations`
4. Run `make migrate`
5. Run `pytest .`

## Acceptance criteria

- Indexes added on `sale_date`, `create_date`, and `is_recurring`
- Migration generated and applied
- Tests pass
