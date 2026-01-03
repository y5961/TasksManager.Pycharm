
from django.contrib import admin
from django.urls import path,include
from App1 import views

urlpatterns = [
    path("", views.home),
    path("signIn/", views.sign_in),
    path("signUp/", views.sign_up),
    path('create-team/', views.create_team, name='create_team'),
    #path('register-final/', views.register_final, name='register_final'),
    # path("index3/", views.index3, name='index3'),
]
