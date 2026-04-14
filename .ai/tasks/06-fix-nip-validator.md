# Task 06: Refactor NIP and ZIP code validators

## Priority: HIGH
## Status: done
## Estimated scope: small

## Problem

The `nip_validator` accepted letters and had an overly broad range (8–16 characters). A Polish NIP is exactly 10 digits. Foreign companies need a separate, more permissive validator. ZIP code validation was also hardcoded to Polish format only.

## Files modified

- `base/validators.py` — added `polish_nip_validator`, `foreign_nip_validator`, `polish_zip_code_validator`, `foreign_zip_code_validator`
- `companies/models.py` — `clean()` now calls validators from `base/validators.py` based on country
- `persons/models.py` — same pattern; `nip` guard kept because the field is nullable

## What was implemented

- `polish_nip_validator` — `RegexValidator` enforcing exactly 10 digits
- `foreign_nip_validator` — callable class stripping spaces/dashes, then checking 4–20 alphanumeric chars
- `polish_zip_code_validator` — `RegexValidator` enforcing `XX-XXX` format
- `foreign_zip_code_validator` — `RegexValidator` allowing 2–15 alphanumeric chars, dashes, spaces
- `Company.clean()` selects Polish or foreign validators based on `self.country.country.lower() == "polska"`
- Shared `_validate_address_fields()` helper extracted to keep `clean()` within flake8 complexity limit (C901 ≤ 10)

## Acceptance criteria (met)

- Polish NIP validated as exactly 10 digits
- Foreign NIP validated as 4–20 alphanumeric characters
- Polish ZIP validated as `XX-XXX`
- Validators live in `base/validators.py`, not in model files
- All tests pass (`pytest companies/ persons/`)
- `black`, `isort`, `flake8` pass
