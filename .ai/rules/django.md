# Django rules

- Python 3.12, Django 5.2, DRF 3.15
- Custom User model (`users.User`) — email as USERNAME_FIELD, not username
- All data is user-scoped — every query MUST filter by `request.user`. Never create queries that leak data between users
- Function-based views with `@login_required` decorator
- Form-based validation — never process raw `request.POST` directly
- Celery 5.4 + Redis for async tasks. Periodic tasks registered in `base/settings/common.py` CELERY_BEAT_SCHEDULE
- PostgreSQL 15 in production, SQLite in tests
- Settings split: `base/settings/common.py` (shared), `dev.py`, `production.py`, `test.py`
- i18n: UI strings wrapped in `gettext_lazy`. App language is Polish, code is English
