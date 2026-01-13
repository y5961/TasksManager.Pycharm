
from django.contrib import admin
from django.urls import path,include
from App1 import views

urlpatterns = [
    path("", views.home),
    path("sign-in/", views.sign_in,name="sign_in"),
    path("sign-up/", views.sign_up,name="sign_up"),
    path('create-team/', views.create_team, name='create_team'),
    path('team-management/', views.team_management, name='team_management'),
    path('select-team/', views.select_team, name='select_team'),
    path('add-task/', views.add_task, name='add_task'),
    path('delete-task/<int:task_id>', views.delete_task, name='delete_task'),
    path('edit-task/<int:task_id>/', views.edit_task, name='edit_task'),
    path('update-owner/<int:task_id>/', views.update_owner, name='update_owner'),
    path('update-status/<int:task_id>/', views.update_status, name='update_status'),
    path("logout/", views.log_out, name="log_out"),
    # path('filter-tasks/<int:task_id>/', views.filter_tasks, name='filter_tasks'),

]
