# apps/users/urls.py
from django.urls import path
from .views import (
    RegistrationAPIView,
    LoginAPIView,
    VerifyEmailAPIView,
    GenerateNewOTPView,
)
from .views import LogoutAPIView, ForgotPasswordAPIView, ResetPasswordAPIView

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("verify/", VerifyEmailAPIView.as_view(), name="email-verify"),
    path("verify/otp/", GenerateNewOTPView.as_view(), name="generate-otp"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="forgot-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="reset-password"),
]
