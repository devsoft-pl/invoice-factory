from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from persons.forms import PersonFilterForm, PersonForm
from persons.models import Person
from persons.utils import get_user_person_or_404


@login_required
def list_persons_view(request):
    persons_list = Person.objects.filter(user=request.user)

    filter_form = PersonFilterForm(request.GET)
    if filter_form.is_valid():
        persons_list = filter_form.get_filtered_persons(persons_list)

    total_persons = persons_list.count()

    paginator = Paginator(persons_list, 10)
    page = request.GET.get("page")
    try:
        persons = paginator.page(page)
    except PageNotAnInteger:
        persons = paginator.page(1)
    except EmptyPage:
        persons = paginator.page(paginator.num_pages)

    context = {
        "persons": persons,
        "total_persons": total_persons,
        "filter_form": filter_form,
        "current_module": "persons",
    }
    return render(request, "persons/list_persons.html", context)


@login_required
def detail_person_view(request, person_id):
    queryset = Person.objects.select_related("user", "country")
    person = get_object_or_404(queryset, pk=person_id)

    if person.user != request.user:
        raise Http404(_("Person does not exist"))

    context = {"person": person}
    return render(request, "persons/detail_person.html", context)


@login_required
def create_person_view(request):
    if request.method != "POST":
        form = PersonForm(current_user=request.user)
    else:
        form = PersonForm(current_user=request.user, data=request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.user = request.user
            person.save()
            return redirect("persons:list_persons")

    context = {"form": form}
    return render(request, "persons/create_person.html", context)


@login_required
def create_person_ajax_view(request):
    if request.method != "POST":
        form = PersonForm(current_user=request.user)
    else:
        form = PersonForm(current_user=request.user, data=request.POST)
        if form.is_valid():
            person = form.save(commit=False)
            person.user = request.user
            person.save()
            return JsonResponse(
                {
                    "success": True,
                    "id": person.id,
                    "name": f"{person.first_name.capitalize()} "
                    f"{person.last_name.capitalize()}",
                }
            )
        else:
            return JsonResponse({"success": False, "errors": form.errors})

    context = {"form": form}
    return render(request, "persons/create_person_ajax.html", context)


@login_required
def replace_person_view(request, person_id):
    person = get_user_person_or_404(person_id, request.user)

    if request.method != "POST":
        form = PersonForm(current_user=request.user, instance=person)
    else:
        form = PersonForm(current_user=request.user, instance=person, data=request.POST)

    if form.is_valid():
        form.save()
        return redirect("persons:list_persons")

    context = {"person": person, "form": form}
    return render(request, "persons/replace_person.html", context)


@login_required
def delete_person_view(request, person_id):
    person = get_user_person_or_404(person_id, request.user)
    person.delete()

    return redirect("persons:list_persons")
