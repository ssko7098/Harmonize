from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_list, name="user_list"),
    path('register/', views.register, name='register'),
    path('profile/<int:pk>/', views.profile, name='profile'),
]