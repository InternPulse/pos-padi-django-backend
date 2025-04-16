# # all URLs that are related to authentication
# from django.urls import path, include
# from dj_rest_auth.views import (
#     LoginView,
#     LogoutView,
#     PasswordChangeView,
#     PasswordResetView,
#     PasswordResetConfirmView,
# )
# from rest_framework_simplejwt.views import TokenRefreshView



# urlpatterns = [
#     path(
#         "password/reset/",
#         PasswordResetView.as_view(),
#         name="password_reset",
#     ),
#     path(
#         "password/reset/confirm/uidb64/token/",
#         PasswordResetConfirmView.as_view(),
#         name="password_rest_confirm",
#     ),
#     path("login/", LoginView.as_view(), name="login"),
#     path("logout/", LogoutView.as_view(), name="logout"),
#     path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
#     path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    
# ]
