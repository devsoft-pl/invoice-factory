from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from summary_recipients.forms import SummaryRecipientForm
from summary_recipients.models import SummaryRecipient
from summary_recipients.utils import (
    get_user_company_or_404,
    get_user_summary_recipient_or_404,
)


@login_required
def list_summary_recipients_view(request, company_id):
    company = get_user_company_or_404(company_id, request.user)
    summary_recipients = SummaryRecipient.objects.filter(
        company=company
    ).select_related("company")

    context = {"company": company, "summary_recipients": summary_recipients}
    return render(request, "summary_recipients/list_summary_recipients.html", context)


@login_required
def create_summary_recipient_view(request, company_id):
    company = get_user_company_or_404(company_id, request.user)

    if request.method != "POST":
        form = SummaryRecipientForm()
    else:
        form = SummaryRecipientForm(data=request.POST)
        if form.is_valid():
            month_summary_recipient = form.save(commit=False)
            month_summary_recipient.company = company
            month_summary_recipient.save()
            return redirect("summary_recipients:list_summary_recipients", company.pk)

    context = {"form": form, "company": company}
    return render(request, "summary_recipients/create_summary_recipient.html", context)


@login_required
def replace_summary_recipient_view(request, summary_recipient_id):
    summary_recipient = get_user_summary_recipient_or_404(
        summary_recipient_id, request.user
    )

    if request.method != "POST":
        form = SummaryRecipientForm(instance=summary_recipient)
    else:
        form = SummaryRecipientForm(instance=summary_recipient, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                "summary_recipients:list_summary_recipients",
                summary_recipient.company.pk,
            )

    context = {
        "summary_recipient": summary_recipient,
        "form": form,
        "company": summary_recipient.company,
    }
    return render(request, "summary_recipients/replace_summary_recipient.html", context)


@login_required
def delete_summary_recipient_view(request, summary_recipient_id):
    summary_recipient = get_user_summary_recipient_or_404(
        summary_recipient_id, request.user
    )
    summary_recipient.delete()

    return redirect(
        "summary_recipients:list_summary_recipients", summary_recipient.company.pk
    )
