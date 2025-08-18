from django.urls import path
from .views import *
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
    path('logout/', logout_page, name='logout_page'),
    path('verification-sent/', verification_sent, name='verification_sent'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('password-reset/', reset_password_view, name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='reset_password/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='reset_password/password_reset_complete.html'),
         name='password_reset_complete'),
    path('profile/', profile, name='profile'),
    path('profile-update/', profile_update, name='profile_update'),
    path('toggle-dark-mode/', toggle_dark_mode, name='toggle_dark_mode'),
]