# Task 08: Add rate limiting to the REST API

## Priority: MEDIUM
## Status: todo
## Estimated scope: tiny

## Problem

Token authentication has no throttling. The `/api-token-auth/` endpoint is vulnerable to brute-force attacks.

## Files to modify

- `base/settings/common.py` — `REST_FRAMEWORK` section

## Steps

1. Read `base/settings/common.py` — find the `REST_FRAMEWORK` dict
2. Add throttling configuration:
   ```python
   REST_FRAMEWORK = {
       ...existing config...
       "DEFAULT_THROTTLE_CLASSES": [
           "rest_framework.throttling.AnonRateThrottle",
           "rest_framework.throttling.UserRateThrottle",
       ],
       "DEFAULT_THROTTLE_RATES": {
           "anon": "20/minute",
           "user": "100/minute",
       },
   }
   ```
3. Run `pytest .` — verify that API tests do not fail due to throttling (each test has its own request count, but double-check)

## Acceptance criteria

- Anonymous requests throttled to 20 per minute
- Authenticated users throttled to 100 per minute
- Existing tests pass
