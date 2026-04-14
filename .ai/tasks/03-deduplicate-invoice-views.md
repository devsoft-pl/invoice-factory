# Task 03: Eliminate duplication in invoice views

## Priority: HIGH
## Status: todo
## Estimated scope: medium

## Problem

`invoices/views.py` contains massive duplication:
- 4 invoice creation views with identical structure
- 2 duplication views with identical logic
- 2 edit/correction views with identical logic
- Permission checks (company.user / person.user) copied in every view

## Files to modify

- `invoices/views.py` — main file to refactor

## Steps

1. Read the full `invoices/views.py`
2. Extract a permission-checking helper:
   ```python
   def get_user_invoice_or_404(request, invoice_id, queryset=None):
       """Fetches an invoice and verifies it belongs to request.user."""
       if queryset is None:
           queryset = Invoice.objects.select_related("company", "person", "client")
       invoice = get_object_or_404(queryset, pk=invoice_id)
       user = get_user_from_invoice(invoice)
       if user != request.user:
           raise Http404(_("Invoice does not exist"))
       return invoice
   ```
3. Replace the repeated if/elif/else blocks in each view with a call to this helper
4. Extract shared duplication logic:
   ```python
   def _duplicate_invoice(request, invoice_id, form_class, template_name):
       """Shared logic for duplicate_company and duplicate_individual."""
       ...
   ```
5. Make `duplicate_company_invoice_view` and `duplicate_individual_invoice_view` thin wrappers calling the shared function
6. Apply the same pattern to `replace_sell_invoice_view` and `replace_sell_person_to_client_invoice_view`
7. Run `pytest invoices/` after each change — do not break existing tests

## Constraints

- Do NOT convert FBVs to CBVs — that is too large a change at this point
- Preserve existing URL patterns and view names (public API must not change)
- Keep existing templates unchanged — only `views.py` is modified

## Acceptance criteria

- Zero repeated permission-checking blocks
- Invoice duplication handled by a single shared function
- Edit/correction handled by a single shared function
- All tests pass
- `flake8` and `black` pass
