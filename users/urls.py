from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-email/', views.verify_email, name='verify-email'),
    path('profile/', views.profile_page, name='profile'),

    # API route
    path('api/profile/', views.ProfileAPIView.as_view(), name='api-profile'),
    path('api/forgot-password/', views.PasswordResetRequestAPIView.as_view(), name='api-forgot-password'),

    # Password reset GUI
    path('forgot-password/', views.forgot_password_page, name='forgot-password'),
    path('reset-password/', views.reset_password_page, name='reset-password'),
]
