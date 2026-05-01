# Task 13: Reduce Sentry traces_sample_rate

## Priority: LOW
## Status: todo
## Estimated scope: tiny

## Problem

`traces_sample_rate=1.0` in Sentry configuration — 100% sampling in production is costly and adds unnecessary overhead.

## Files to modify

- `base/settings/common.py`

## Steps

1. Read `base/settings/common.py` — find the `sentry_sdk.init(...)` block
2. Change to:
   ```python
   sentry_sdk.init(
       dsn=SENTRY_DSN,
       integrations=[DjangoIntegration()],
       traces_sample_rate=float(env("SENTRY_TRACES_SAMPLE_RATE", default="0.1")),
       send_default_pii=True,
   )
   ```
3. Add `SENTRY_TRACES_SAMPLE_RATE=0.1` to `.env.example`
4. Run `pytest .`

## Acceptance criteria

- Default sample rate is 10% (0.1)
- Configurable via environment variable
- `.env.example` updated
