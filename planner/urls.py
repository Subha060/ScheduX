from django.urls import path
from . import views

urlpatterns = [
    path("planner/", views.planner_view, name="planner"),
    path("planner/goals/create/", views.create_goal, name="create_goal"),
    path("planner/goals/update/", views.update_goal, name="update_goal"),
    path("planner/goals/delete/", views.delete_goal, name="delete_goal"),
    path("planner/timeblocks/create/", views.create_timeblock, name="create_timeblock"),
    path("planner/focus/update/", views.update_focus, name="update_focus"),
]
