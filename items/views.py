from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render

from items.forms import ItemForm
from items.models import Item


@login_required
def list_items_view(request):
    items = Item.objects.all()
    context = {"items": items}
    return render(request, "list_items.html", context)


@login_required
def detail_item_view(request, item_id):
    item = Item.objects.filter(pk=item_id).first()
    if not item:
        raise Http404("Item does not exist")
    context = {"item": item}
    return render(request, "detail_item.html", context)


@login_required
def create_item_view(request):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = ItemForm(initial=initial)
    else:
        form = ItemForm(data=request.POST)
        if form.is_valid():
            form.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            return redirect("items:list_items")

    context = {"form": form}
    return render(request, "create_item.html", context)


@login_required
def replace_item_view(request, item_id):
    item = Item.objects.filter(pk=item_id).first()
    if not item:
        raise Http404("Item does not exist")

    if request.method != "POST":
        form = ItemForm(instance=item)
    else:
        form = ItemForm(instance=item, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect("items:list_items")

    context = {"item": item, "form": form}
    return render(request, "replace_item.html", context)


@login_required
def delete_item_view(request, item_id):
    item = Item.objects.filter(pk=item_id).first()
    if not item:
        raise Http404("Item does not exist")

    item.delete()
    return redirect("items:list_items")
