# apps/users/urls.py
from django.urls import path
from .views import (
    RegistrationAPIView,
    LoginAPIView,
    VerifyEmailAPIView,
    GenerateNewOTPView,
    UserSummaryView,
    ChangePasswordAPIView,
    LogoutAPIView,
    ForgotPasswordAPIView,
    ResetPasswordAPIView,
    RefreshTokenAPIView,
    PushNotificationSettingButton,
    EmailToggleSettingButton,
    UserProfileUpdate,
)

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("verify/", VerifyEmailAPIView.as_view(), name="email-verify"),
    path("verify/otp/", GenerateNewOTPView.as_view(), name="generate-otp"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
    path("refresh-token/", RefreshTokenAPIView.as_view(), name="refresh-token"),
    path("summary/", UserSummaryView.as_view(), name="user-summary"),
    path("change-password/", ChangePasswordAPIView.as_view(), name="change-password"),
    path(
        "push-notification-setting/",
        PushNotificationSettingButton.as_view(),
        name="push-notification-setting",
    ),
    path(
        "email-toggle-setting/",
        EmailToggleSettingButton.as_view(),
        name="email-toggle-setting",
    ),
    path("update-profile/", UserProfileUpdate.as_view(), name="update-profile"),
]
