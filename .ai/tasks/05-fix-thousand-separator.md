# Task 05: Fix THOUSAND_SEPARATOR setting

## Priority: HIGH
## Status: todo
## Estimated scope: tiny

## Problem

`THOUSAND_SEPARATOR = "$"` in `base/settings/common.py`. A dollar sign as a thousands separator in a Polish financial application is an obvious mistake.

## Files to modify

- `base/settings/common.py`

## Steps

1. Read `base/settings/common.py` — find the `THOUSAND_SEPARATOR` line
2. Change `THOUSAND_SEPARATOR = "$"` to `THOUSAND_SEPARATOR = "\u00a0"` (non-breaking space — Polish standard per PN-EN)
3. Grep templates (`templates/`) and code for any hardcoded amount formatting that depends on this separator
4. Run `pytest .`

## Acceptance criteria

- `THOUSAND_SEPARATOR` is a non-breaking space (or regular space)
- Amount formatting in templates looks correct
- Tests pass
