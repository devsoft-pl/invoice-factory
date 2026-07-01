# Code style rules

## Formatting (enforced by CI)
- **black**: line length 88, excludes migrations/venv/.git
- **isort**: profile=black, same exclusions
- **flake8**: max-line-length=120, max-complexity=10, extend-ignore=E203
- All three MUST pass before code is considered complete
- **After every task**: run `poetry run black <files> && poetry run isort <files> && poetry run flake8 <files>` on all modified files

## Model field guards
- Before adding `if self.field:` guards in `clean()` or validators, check whether the field is actually optional (`null=True`, `blank=True`)
- Required fields (`CharField` without `null=True`/`blank=True`) are guaranteed non-empty by the time `clean()` runs — skip the guard

## Naming
- Models: singular (`Invoice`, `Company`, `Person`)
- Apps: plural (`invoices`, `companies`, `persons`)
- Views: `{action}_{noun}_view()` — e.g. `list_invoices_view`, `detail_company_view`
- Celery tasks: `{verb}_{noun}` — e.g. `create_invoices_for_recurring`
- Templates: `templates/{app_name}/{action}_{noun}.html`

## Commits
Conventional Commits with semantic-release:
- `feat:` — new feature (minor bump)
- `fix:` — bug fix (patch bump)
- `refactor:`, `perf:`, `chore:`, `ci:`, `docs:`, `style:`, `build:`, `revert:` — patch bump
