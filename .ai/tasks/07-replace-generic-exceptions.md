# Task 07: Replace generic exceptions with Http404

## Priority: MEDIUM
## Status: done
## Estimated scope: tiny

## Problem

Several views raised `Exception("This should not have happened")` when an invoice had neither a company nor a person. In production this returned a 500 response, potentially leaking HTML or a stack trace.

## Files modified

- `invoices/views.py` — all occurrences of `raise Exception` replaced with `raise Http404`

## What was implemented

Every `raise Exception(...)` in `invoices/views.py` was replaced with:
```python
raise Http404(_("Invoice does not exist"))
```

`Http404` was already imported. No new imports were needed.

## Acceptance criteria (met)

- Zero `raise Exception` in `invoices/views.py`
- Missing invoice returns 404, not 500
- Tests pass
