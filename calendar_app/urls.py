from django.urls import path
from . import views

urlpatterns = [
    path("", views.calendar_view, name="calendar"),
    path("api/create/", views.create_event, name="create_event"),
    path("api/update/", views.update_event, name="update_event"),
    path("api/delete/", views.delete_event, name="delete_event"),
]
