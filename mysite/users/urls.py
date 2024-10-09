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
    path('profile_settings/', views.profile_settings_view, name='profile_settings'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('accounts/confirm-email/<str:key>/', views.CustomConfirmEmailView.as_view(), name='account_confirm_email'),
]
