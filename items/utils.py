from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from items.models import Item

def get_user_item_or_404(item_id, user):
    item = get_object_or_404(
        Item.objects.select_related("invoice__company__user", "invoice__person__user", "invoice"),
        pk=item_id,
    )
    if item.invoice.company:
        if item.invoice.company.user != user:
            raise Http404(_("Item does not exist"))
    elif item.invoice.person:
        if item.invoice.person.user != user:
            raise Http404(_("Item does not exist"))
    else:
        raise Exception(_("This should not have happened"))
    return item