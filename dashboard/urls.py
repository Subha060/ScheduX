from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("chat/", views.chat, name="chat"),
    path("email/", views.email_view, name="email"),
    path("activity/", views.activity_view, name="activity"),
    path("summaries/", views.summaries_view, name="summaries"),
    path("summaries/delete/<int:summary_id>/", views.delete_summary, name="delete_summary"),
]
