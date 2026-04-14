# Task 15: KSeF integration — fetch purchase invoices

## Priority: MEDIUM
## Status: done
## Estimated scope: medium

## Problem

No integration with KSeF (Krajowy System e-Faktur). Purchase invoices (where the company is the buyer) should be fetched automatically from KSeF in the background via a Celery task.

## KSeF environment

- Test: `https://api-test.ksef.mf.gov.pl`
- Production: `https://api.ksef.mf.gov.pl`
- Swagger: `https://api-test.ksef.mf.gov.pl/docs/v2/index.html`
- OpenAPI spec saved locally: `invoices/adapters/ksef_openapi.json`

## Files created / modified

- `base/settings/common.py` — `KSEF_*` settings + entry in `CELERY_BEAT_SCHEDULE`
- `companies/models.py` — added `ksef_token` and `ksef_last_fetched_at` fields
- `companies/migrations/0013_company_ksef_last_fetched_at_company_ksef_token.py` — migration
- `invoices/adapters/ksef_adapter.py` — KSeF REST adapter with full auth flow
- `invoices/adapters/ksef_mapper.py` — maps KSeF metadata + XML to Invoice/Item dicts
- `invoices/adapters/ksef_xml_mapper.py` — parses FA(3) XML (items, payment data)
- `invoices/adapters/ksef_openapi.json` — OpenAPI spec for local reference
- `invoices/tasks.py` — new Celery task `fetch_purchase_invoices_from_ksef`

## What was implemented

### Authentication flow (`ksef_adapter.py`)
Full 3-step async auth:
1. `GET /api/v2/security/public-key-certificates` — fetch RSA public key
2. `POST /api/v2/auth/challenge` — get `challenge` + `timestampMs`
3. Encrypt `"{token}|{timestampMs}"` with RSA-OAEP SHA-256
4. `POST /api/v2/auth/ksef-token` → `referenceNumber` + `authenticationToken`
5. Poll `GET /api/v2/auth/{referenceNumber}` until `status.code == 200`
6. `POST /api/v2/auth/token/redeem` → `accessToken` stored as `self.session_token`

### Invoice fetching
- `get_purchase_invoices()` — `POST /api/v2/invoices/query/metadata` with `subjectType: "Subject2"`, `dateType: "Issue"`, ISO-8601 datetime range
- `get_invoice_xml()` — `GET /api/v2/invoices/ksef/{ksefNumber}` returning FA(3) XML
- `get_all_purchase_invoices()` — generator yielding pages of 100 invoices

### XML parsing (`ksef_xml_mapper.py`)
- Namespace: `http://crd.gov.pl/wzor/2025/06/25/13775/`
- `map_ksef_xml_to_items()` — parses `FaWiersz` elements → name, amount, net_price, vat_rate
- `map_ksef_xml_to_payment()` — parses `Platnosc/NrRachunku` → account_number, payment_method

### Celery task (`tasks.py`)
- Iterates over companies with `is_my_company=True` and a non-null `ksef_token`
- Starts from `ksef_last_fetched_at` or `2026-01-01` on first run
- Processes day by day, updates `ksef_last_fetched_at` after each day (resumable on failure)
- Saves Invoice + Items in `transaction.atomic()`, calls `invoice.update_totals()`
- Skips invoices that already exist (by `invoice_number` + `company`)
- `get_or_create` for Currency and VatRate

## Acceptance criteria (met)

- `KSEF_IS_TEST`, `KSEF_API_URL_TEST`, `KSEF_API_URL_PRODUCTION` in settings
- `Company.ksef_token` — optional CharField(max_length=255)
- `Company.ksef_last_fetched_at` — optional DateField
- Full authentication flow implemented and tested against the test environment
- `get_purchase_invoices()` uses correct enum values (`Subject2`, `Issue`) and ISO-8601 datetime format
- Task registered in `CELERY_BEAT_SCHEDULE` (daily at 08:00)
- Day-by-day iteration with resumable `ksef_last_fetched_at` checkpoint
- Invoice + Items persisted atomically; duplicates skipped

## References

- Swagger: https://api-test.ksef.mf.gov.pl/docs/v2/index.html
- FA(3) schema namespace: `http://crd.gov.pl/wzor/2025/06/25/13775/`
