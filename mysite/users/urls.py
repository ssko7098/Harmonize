from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_view, name='search'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('delete_song/<int:song_id>/', views.delete_song, name='delete_song'),
    path('profile_settings/', views.profile_settings_view, name='profile_settings'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin_dashboard/manage_songs/', views.manage_songs, name='manage_songs'),
    path('admin_dashboard/reported_comments/', views.manage_reported_comments, name='reported_comments'),
]
