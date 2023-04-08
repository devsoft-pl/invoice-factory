from django.urls import path

from items.views import (create_item_view, detail_item_view, list_items_view,
                         replace_item_view)

app_name = "items"
urlpatterns = [
    path("", list_items_view, name="list_items"),
    path("<int:item_id>/", detail_item_view, name="detail_item"),
    path("create/", create_item_view, name="create_item"),
    path("replace/<int:item_id>/", replace_item_view, name="replace_item"),
]
