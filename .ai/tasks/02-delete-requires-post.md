# Task 02: Restrict delete views to POST requests only

## Priority: CRITICAL
## Status: todo
## Estimated scope: small

## Problem

`delete_invoice_view` accepts GET requests — a link, crawler, or browser prefetch could accidentally delete an invoice.

## Files to modify

- `invoices/views.py` — `delete_invoice_view`
- `invoices/urls.py` — verify route
- `templates/invoices/` — confirmation template may be needed
- Check delete views in: `companies/views.py`, `persons/views.py`, `items/views.py`, `currencies/views.py`, `countries/views.py`, `vat_rates/views.py`, `accountants/views.py`, `summary_recipients/views.py`

## Steps

1. Read `invoices/views.py` — find `delete_invoice_view`
2. Add `require_POST` decorator or a `request.method != "POST"` check:
   ```python
   from django.views.decorators.http import require_POST

   @login_required
   @require_POST
   def delete_invoice_view(request, invoice_id):
       ...
   ```
3. Find delete links in templates — replace `<a href="...delete...">` with a form:
   ```html
   <form method="post" action="{% url 'invoices:delete_invoice' invoice.pk %}">
       {% csrf_token %}
       <button type="submit">Delete</button>
   </form>
   ```
4. Repeat steps 1–3 for every app that has a delete view
5. Run `pytest .` — update tests that use `client.get()` on delete URLs to use `client.post()` instead

## Acceptance criteria

- All delete views require POST
- GET on a delete URL returns 405 Method Not Allowed
- Templates use forms with CSRF token instead of plain links
- Tests updated and passing
