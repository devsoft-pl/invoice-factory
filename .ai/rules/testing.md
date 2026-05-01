# Testing rules

- Framework: pytest + pytest-django + factory-boy + parameterized
- Settings: `base.settings.test` (SQLite in-memory)
- Config: `pytest.ini` — DJANGO_SETTINGS_MODULE=base.settings.test
- Run: `pytest .` or `make test_all`
- Coverage target: 100% (excludes migrations, config)

## Conventions
- Use Factory Boy factories for ALL test data — never create objects manually
- Mock external APIs (NBP, CEIDG) — never call real APIs in tests
- Use `parameterized` for data-driven test variations
- All view tests require authenticated user (login_required)
- Test both happy path and edge cases
- Tests location: `{app}/tests/test_{module}.py`
- After writing code, always run `pytest .` to verify nothing is broken
