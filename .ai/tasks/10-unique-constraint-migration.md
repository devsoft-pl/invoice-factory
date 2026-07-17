# Task 10: Migrate unique_together to UniqueConstraint

## Priority: LOW
## Status: todo
## Estimated scope: small

## Problem

`unique_together` has been deprecated since Django 4.2. The recommended approach is `Meta.constraints` with `UniqueConstraint`.

## Files to modify

- `invoices/models.py` — Invoice (invoice_number + company), Year (year + user)
- `companies/models.py` — Company (nip + regon + user)
- `currencies/models.py` — Currency (code + user)
- `vat_rates/models.py` — VatRate (rate + user)
- `countries/models.py` — Country (country + user)
- `persons/models.py` — check for any `unique_together`

## Steps

1. Grep `unique_together` across all models
2. For each model, replace:
   ```python
   # BEFORE:
   class Meta:
       unique_together = ["field_a", "field_b"]

   # AFTER:
   class Meta:
       constraints = [
           models.UniqueConstraint(
               fields=["field_a", "field_b"],
               name="%(app_label)s_%(class)s_unique_field_a_field_b",
           ),
       ]
   ```
3. Use naming convention: `{app}_{model}_unique_{fields}` e.g. `invoices_invoice_unique_number_company`
4. Run `make makemigrations` — a migration should be generated for each changed app
5. Run `make migrate`
6. Run `pytest .`

## Constraints

- The migration must be safe — Django handles the transition automatically (drops old constraint, adds new)
- Do not change any logic — only the declaration form

## Acceptance criteria

- Zero `unique_together` in the codebase
- All unique constraints declared via `UniqueConstraint`
- Migrations generated and applied successfully
- Tests pass
