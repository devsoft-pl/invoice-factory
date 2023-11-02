from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from companies.models import Company
from summary_recipients.forms import SummaryRecipientForm
from summary_recipients.models import SummaryRecipient


@login_required
def list_summary_recipients_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)
    summary_recipients = SummaryRecipient.objects.filter(company=company)

    if company.user != request.user:
        raise Http404(_("Company does not exist"))

    context = {"company": company, "summary_recipients": summary_recipients}

    return render(request, "summary_recipients/list_summary_recipients.html", context)


@login_required
def create_summary_recipient_view(request, company_id):
    company = get_object_or_404(Company, pk=company_id)

    if company.user != request.user:
        raise Http404(_("Company does not exist"))

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
    summary_recipient = get_object_or_404(SummaryRecipient, pk=summary_recipient_id)

    if summary_recipient.company.user != request.user:
        raise Http404(_("Summary recipient does not exist"))

    if request.method != "POST":
        form = SummaryRecipientForm(instance=summary_recipient)
    else:
        form = SummaryRecipientForm(instance=summary_recipient, data=request.POST)

        if form.is_valid():
            form.save()

        return redirect(
            "summary_recipients:list_summary_recipients", summary_recipient.company.pk
        )

    context = {
        "summary_recipient": summary_recipient,
        "form": form,
        "company": summary_recipient.company,
    }
    return render(request, "summary_recipients/replace_summary_recipient.html", context)


@login_required
def delete_summary_recipient_view(request, summary_recipient_id):
    summary_recipient = get_object_or_404(SummaryRecipient, pk=summary_recipient_id)

    if summary_recipient.company.user != request.user:
        raise Http404(_("Summary recipient does not exist"))

    summary_recipient.delete()

    return redirect(
        "summary_recipients:list_summary_recipients", summary_recipient.company.pk
    )
