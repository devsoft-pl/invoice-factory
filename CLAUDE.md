# CLAUDE.md — AI Instructions for Invoice Factory

## Project Overview

**Invoice Factory** is a Django web application for managing invoices for Polish companies and individuals. It supports sales/purchase invoices, recurring billing, multi-currency with NBP exchange rates, PDF generation, and automated email reporting.

- **Repository**: devsoft-pl/invoice-factory
- **Version**: 1.7.0 (semantic-release)
- **Language**: Polish (pl), timezone Europe/Warsaw, base currency PLN
- **Live**: https://invoice-factory.devsoft.pl/

## Tech Stack

- Python 3.12, Django 5.2, Django REST Framework 3.15
- PostgreSQL 15 (production), SQLite (tests)
- Celery 5.4 + Redis (async tasks)
- xhtml2pdf (PDF generation), num2words (amounts in Polish words)
- AWS S3 / MinIO (static & media storage in production)
- Docker + Kubernetes (ArgoCD via GitOps)
- Sentry (error tracking)

## Quick Commands

```bash
# Development
make runserver                  # python manage.py runserver
make migrate                    # python manage.py migrate
make makemigrations             # python manage.py makemigrations
make createsuperuser            # python manage.py createsuperuser
make postgres                   # docker compose up postgres -d
make postgres-down              # docker compose down postgres

# Testing
make test_all                   # pytest .
make coverage_html              # coverage run -m pytest && coverage html

# Linting (all must pass CI)
black --check .                 # Code formatting
flake8                          # Linting (max-line-length=120, max-complexity=10)
isort --check-only .            # Import sorting (profile=black)

# Celery
make celery_worker              # celery -A base.celery worker -l info
make celery_beat                # celery -A base.celery beat -l info

# i18n
make makemessages               # Extract Polish translation strings
make compilemessages            # Compile .po -> .mo files
```

## Project Structure

```
base/                   # Django project config
  settings/
    common.py           # Shared settings
    dev.py              # Development (DEBUG=True, local storage)
    production.py       # Production (S3, Sentry, email)
    test.py             # Tests (SQLite, in-memory)
  urls.py               # Main URL routing
  urls_api.py           # DRF router (/api/*)
  celery.py             # Celery app config
  validators.py         # Custom validators (NIP, REGON, PESEL, etc.)
  mixins.py             # Shared model/view mixins
  storages.py           # S3 storage backends

invoices/               # Core app — invoice CRUD, PDF, recurring logic
companies/              # Company management (own companies + clients)
items/                  # Invoice line items (linked to invoices via FK)
persons/                # Individual contacts (freelancers)
currencies/             # Multi-currency + NBP exchange rates
vat_rates/              # VAT rate management
countries/              # Country reference data
users/                  # Custom User model (email-based auth)
accountants/            # Accountant contacts
summary_recipients/     # Automated monthly/quarterly email reports
reports/                # Revenue reporting & analytics

templates/              # Django templates (Bootstrap)
locale/                 # Polish translations (.po/.mo)
deployment/             # Docker entrypoint, gunicorn config
```

## Key Architecture Decisions

### Multi-tenant by User
All data is scoped to `request.user`. Every model (Company, Person, Currency, VatRate, Country, Invoice) has a FK to User. Queries always filter by the current user. Unique constraints include the user field.

### Custom User Model
`users.User` uses **email as USERNAME_FIELD** (not username). Custom `UserManager` handles user creation.

### Invoice Workflow
- **Types**: Sales (0), Purchase (1)
- **Payment methods**: Bank Transfer (0), Cash (1)
- **Recurring**: `is_recurring` flag + Celery task clones invoices monthly
- **Corrections**: Linked via `CorrectionInvoiceRelation` (one-to-one), number ends with `/k`
- **Settlement**: `is_settled` locks invoice from editing; set by summary recipient with `final_call=True`
- **PDF**: Generated on-demand via xhtml2pdf from `templates/invoices/pdf_invoice.html`

### Item Calculations
Items compute amounts via properties (not stored):
- `net_amount = amount * net_price`
- `tax_amount = (net_amount * vat.rate) / 100`
- `gross_amount = net_amount + tax_amount`

Invoice totals are recalculated via `post_save`/`post_delete` signals on Item.

### Year Tracking
`Year` model auto-created/deleted via Invoice signals. Used for report year filtering.

### External APIs
- **CEIDG**: Polish business registry — fetch company data by NIP (`companies/govs_adapters/`)
- **NBP**: National Bank of Poland — daily exchange rates (`currencies/nbp_adapter.py`)

## Coding Conventions

### Style
- **black**: line length 88, excludes migrations/venv/.git
- **isort**: profile=black, same exclusions
- **flake8**: max-line-length=120, max-complexity=10, extend-ignore=E203
- All three must pass in CI before merge

### Naming
- Models: singular (`Invoice`, `Company`, `Person`)
- Apps: plural (`invoices`, `companies`, `persons`)
- Views: `{action}_{noun}_view()` (e.g., `list_invoices_view`, `detail_company_view`)
- Celery tasks: `{verb}_{noun}` (e.g., `create_invoices_for_recurring`)
- Templates: `templates/{app_name}/{action}_{noun}.html`

### Patterns Used
- Function-based views with `@login_required` decorator
- Form-based validation (Django forms, not raw request data)
- Custom managers for filtered querysets (e.g., `Company.my_clients`)
- Signals for data consistency (Invoice <-> Year, Item -> Invoice totals)
- Factory Boy for test fixtures
- Celery tasks for all async work (email, PDF, exchange rates)

### Commit Messages
Uses **Conventional Commits** with semantic-release:
- `feat:` — new feature (minor version bump)
- `fix:` — bug fix (patch bump)
- Also: `build`, `chore`, `ci`, `docs`, `perf`, `style`, `refactor`, `revert` (all patch)
- Format: `chore(release): {version}` for releases

## Testing

- **Framework**: pytest + pytest-django + factory-boy + parameterized
- **Settings**: `base.settings.test` (SQLite in-memory)
- **Config file**: `pytest.ini` (DJANGO_SETTINGS_MODULE=base.settings.test)
- **Coverage target**: 100% (excludes migrations, config files)
- **Test location**: each app has `tests/` directory with `test_models.py`, `test_views.py`, `test_forms.py`, `test_tasks.py`, `test_serializers.py`, `test_utils.py`
- **Run**: `pytest .` or `make test_all`

### Test Conventions
- Use Factory Boy factories for all test data creation
- Mock external APIs (NBP, CEIDG) — never call real APIs in tests
- Use `parameterized` for data-driven test variations
- All views tested with authentication (login required)
- Test both happy path and edge cases

## REST API

- **Base path**: `/api/`
- **Auth**: Token authentication via `/api-token-auth/` (POST email + password)
- **Pagination**: LimitOffsetPagination (10 items/page)
- **Filtering**: django-filter
- **ViewSets registered on DefaultRouter**: users, vat_rates, currencies, countries, companies, invoices, items, accountants, summary_recipients, persons
- **API views**: defined in `views_api.py` per app, serializers in `serializers.py`

## CI/CD Pipeline (.github/workflows/cicd.yml)

1. **Lint** — black, flake8, isort checks
2. **Test** — pytest with coverage
3. **Release** (master only) — semantic-release creates tags + CHANGELOG
4. **Build** (master only) — Docker image pushed to ghcr.io/devsoft-pl/invoice-factory
5. **Deploy** (master only) — Updates ArgoCD GitOps repo for Kubernetes deployment

## Environment Variables

See `.env.example` for full list. Key ones:
- `SECRET_KEY`, `DEBUG`, `DATABASE_URL`
- `AWS_*` — S3 storage credentials
- `EMAIL_*` — SMTP configuration
- `CELERY_BROKER_URL` — Redis URL
- `CEIDG_API_TOKEN` — Polish business registry API
- `SENTRY_DSN` — Error tracking

## Important Notes for AI Assistants

1. **Language**: The application UI and data are in Polish. Variable names and code are in English. Keep this convention.
2. **User scoping**: ALWAYS filter data by user. Never create queries that could leak data between users.
3. **Signals**: Be aware that saving an Item triggers Invoice recalculation, and saving an Invoice triggers Year management. Don't break these signal chains.
4. **Migrations**: After any model change, run `make makemigrations` and include the migration file.
5. **Formatting**: Run `black`, `isort`, and check `flake8` before considering code complete. CI will reject non-compliant code.
6. **Tests**: Write tests for all new code. Follow existing patterns with Factory Boy and parameterized tests. Place tests in the appropriate app's `tests/` directory.
7. **i18n**: Wrap user-facing strings in `gettext_lazy`. After adding new strings, run `make makemessages` and update the `.po` file.
8. **PDF templates**: Changes to `pdf_invoice.html` must be tested visually — xhtml2pdf has limited CSS support.
9. **Celery tasks**: Any new periodic task needs to be registered in `base/celery.py` beat schedule.
10. **Dependencies**: Managed with Poetry (`pyproject.toml` + `poetry.lock`). Use `poetry add <package>` to add new dependencies.

## AI Task Specs

Detailed rules and task specifications are in `.ai/`:
- `.ai/rules/` — coding rules to follow for every task (Django, style, testing)
- `.ai/tasks/` — individual improvement tasks with steps, constraints, and acceptance criteria
- See `.ai/README.md` for full structure and usage instructions
