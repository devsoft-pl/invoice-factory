# Task 09: Fix CI — use pytest instead of manage.py test

## Priority: MEDIUM
## Status: done
## Estimated scope: tiny

## Problem

CI was using `poetry run python manage.py test`, but the project is configured for pytest (`pytest.ini`, `conftest.py`, fixtures). Tests relying on pytest fixtures and plugins were not being discovered or run correctly in CI.

## Files modified

- `.github/workflows/cicd.yml` — test step updated to use `poetry run pytest .`

## What was implemented

The CI test step was changed from:
```yaml
run: poetry run python manage.py test
```
to:
```yaml
run: poetry run pytest .
```

## Acceptance criteria (met)

- CI uses `poetry run pytest .` instead of `manage.py test`
- Pipeline passes
