from django.urls import path
from . import views

urlpatterns = [
    path('add_comment/<str:username>/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'), 

]
