from django.urls import path
from . import views

urlpatterns = [
    path('add_comment/<str:username>/', views.add_comment, name='add_comment'),
]
