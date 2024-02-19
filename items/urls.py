from django.urls import path

from items.views import create_item_view, delete_item_view, replace_item_view

app_name = "items"
urlpatterns = [
    path("create/<int:invoice_id>/", create_item_view, name="create_item"),
    path("replace/<int:item_id>/", replace_item_view, name="replace_item"),
    path("delete/<int:item_id>/", delete_item_view, name="delete_item"),
]
