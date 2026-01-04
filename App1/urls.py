
from django.contrib import admin
from django.urls import path,include
from App1 import views

urlpatterns = [
    path("", views.home),
    path("signIn/", views.sign_in),
    path("signUp/", views.sign_up),
    path('create-team/', views.create_team, name='create_team'),
    path('team-management/', views.team_management, name='team_management'),
    path('select-team/', views.select_team, name='select_team'),
    path('add-task/', views.add_task, name='add_task'),
    path('assign-tasks/', views.assign_tasks, name='assign_tasks'),
]
