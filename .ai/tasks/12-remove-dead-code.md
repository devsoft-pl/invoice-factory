# Task 12: Remove dead code — unused Invoice constants

## Priority: LOW
## Status: todo
## Estimated scope: tiny

## Problem

Constants `WEEKLY = 0`, `BIWEEKLY = 1`, `MONTHLY = 2`, `THREE_MONTH = 3` are defined on the `Invoice` model but never referenced anywhere in the codebase.

## Files to modify

- `invoices/models.py`

## Steps

1. Grep the entire project for `WEEKLY`, `BIWEEKLY`, `MONTHLY`, `THREE_MONTH` — confirm they are not used outside their definition
2. Also check templates and any JavaScript files
3. If confirmed unused — remove those 4 lines from the Invoice model
4. Run `pytest .`

## Constraints

- Ensure no migration references these constants
- Check templates and JS before removing

## Acceptance criteria

- Constants removed
- Tests pass
