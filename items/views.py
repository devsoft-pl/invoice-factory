from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from items.forms import ItemForm
from items.models import Item


@login_required
def list_items_view(request):
    items = Item.objects.filter(user=request.user)

    context = {"items": items}
    return render(request, "items/list_items.html", context)


@login_required
def detail_item_view(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if item.user != request.user:
        raise Http404("Item does not exist")

    context = {"item": item}
    return render(request, "items/detail_item.html", context)


@login_required
def create_item_view(request, create_my_item=False):
    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = ItemForm(initial=initial, current_user=request.user)
    else:
        form = ItemForm(data=request.POST, current_user=request.user)

        if form.is_valid():
            item = form.save(commit=False)
            item.user = request.user

            if create_my_item:
                item.is_my_item = True

            item.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            if create_my_item:
                return redirect("users:detail_user", request.user.pk)

            return redirect("items:list_items")

    context = {"form": form}
    return render(request, "items/create_item.html", context)


@login_required
def replace_item_view(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if item.user != request.user:
        raise Http404("Item does not exist")

    if request.method != "POST":
        initial = {"next": request.GET.get("next")}
        form = ItemForm(initial=initial, instance=item, current_user=request.user)
    else:
        form = ItemForm(instance=item, data=request.POST, current_user=request.user)

        if form.is_valid():
            form.save()

            next_url = form.cleaned_data["next"]
            if next_url:
                return redirect(next_url)

            if item.is_my_item:
                return redirect("users:detail_user", request.user.pk)

            return redirect("items:list_items")

    context = {"item": item, "form": form}
    return render(request, "items/replace_item.html", context)


@login_required
def delete_item_view(request, item_id):
    item = get_object_or_404(Item, pk=item_id)


    if item.user != request.user:
        raise Http404("Item does not exist")

    item.delete()

    next_url = request.GET.get("next")
    if next_url:
        return redirect(next_url)

    if item.is_my_item:
        return redirect("users:detail_user", request.user.pk)

    return redirect("items:list_items")
