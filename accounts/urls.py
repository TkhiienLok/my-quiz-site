from django.urls import path
from accounts import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'accounts'

urlpatterns = [
    path('login/', views.user_login, name="login"),
    path('logout/', views.user_logout, name="logout-url"),
    path('signup/', views.signup, name="signup-url"),
    path('profile/', views.ProfileView.as_view(), name="view-profile-url"),
    path('profile/<int:pk>/', views.GuestProfileView.as_view(), name="guest-view-profile"),
    path('profile/edit/', views.ProfileEditView.as_view(), name="edit-profile-url"),
    path('account_activation_sent/', views.account_activation_sent, name='account_activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('change_password_complete/', views.ChangePasswordCompleteView.as_view(), name='change-password-complete'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
        template_name='accounts/change_password.html',
        success_url=reverse_lazy('accounts:change-password-complete')
    ), name='change-password'),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset/form.html',
        email_template_name='accounts/password_reset/email.html',
        subject_template_name='accounts/password_reset/subject.txt',
        success_url=reverse_lazy('accounts:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset/done.html'
    ), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset/confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete')
    ), name='password_reset_confirm'),
    path('password_reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset/complete.html',
    ), name='password_reset_complete'),
]
