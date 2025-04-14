# apps/users/urls.py
from django.urls import path
from .views import RegistrationAPIView, LoginAPIView, VerifyEmailAPIView

urlpatterns = [
    path("register/", RegistrationAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("verify/", VerifyEmailAPIView.as_view(), name="email-verify"),
]
