from django.urls import path
from . import views

urlpatterns = [
    path('add_comment/<str:username>/', views.add_comment, name='add_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'), 
    path('comments/like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('comments/dislike/<int:comment_id>/', views.dislike_comment, name='dislike_comment')
]
