# apps/users/views.py
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.mail import send_mail, BadHeaderError
from django.utils.timezone import now
from django.conf import settings
from datetime import timedelta
import random
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegistrationSerializer, LoginSerializer
from .models import User


def generate_otp(user):
    otp = random.randint(100000, 999999)
    user.otp = otp
    user.otp_expiration = now() + timedelta(seconds=59)
    user.save()
    return otp


class RegistrationAPIView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Register a new user",
        operation_description="This endpoint allows a new user to register by providing their details. An OTP is sent to their email for verification.",
        request_body=RegistrationSerializer,
        responses={
            201: "User registered successfully. Check your email for the OTP to verify your account.",
            400: "Invalid data or bad request.",
            500: "Email sending failed.",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = generate_otp(user)
            try:
                send_mail(
                    subject="Verify Your Email",
                    message=f"Your OTP for email verification is: {otp}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return Response(
                    {"message": "User registered successfully. Check your email for the OTP to verify your account."},
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"error": "An error occurred while processing your request."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Login user",
        operation_description="This endpoint allows a user to log in by providing their email and password. Returns access and refresh tokens.",
        request_body=LoginSerializer,
        responses={
            200: "Login successful. Returns access and refresh tokens.",
            400: "Invalid credentials.",
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)

        # Adding custom claims to the token
        access = refresh.access_token
        access["role"] = user.role

        if user.role == "agent":
            access["agent_id"] = user.agent.agent_id
        elif user.role == "customer":
            access["customer_id"] = user.customer.customer_id
        

        return Response(
            {
                "refresh": str(refresh),
                "access": str(access),
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Verify email",
        operation_description="This endpoint verifies a user's email using the OTP sent to their email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
                "otp": openapi.Schema(type=openapi.TYPE_STRING, description="OTP sent to the user's email"),
            },
            required=["email", "otp"],
        ),
        responses={
            200: "Email verified successfully.",
            400: "Invalid or expired OTP.",
            404: "User not found.",
        },
    )
    def post(self, request, *args, **kwargs):
        otp = request.data.get("otp")
        email = request.data.get("email")

        if not otp or not email:
            return Response({"error": "OTP and email are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.otp != otp or user.otp_expiration < now():
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        user.is_verified = True
        user.otp = None
        user.otp_expiration = None
        user.save()

        return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Logout user",
        operation_description="This endpoint logs out a user by blacklisting their refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token to blacklist"),
            },
            required=["refresh"],
        ),
        responses={
            200: "Logout successful.",
            400: "Invalid or expired token.",
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)


class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Forgot password",
        operation_description="This endpoint sends an OTP to the user's email for password reset.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
            },
            required=["email"],
        ),
        responses={
            200: "OTP sent to your email.",
            404: "User with this email does not exist or is not verified.",
            500: "Failed to send email.",
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_verified=True)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist or is not verified."}, status=status.HTTP_404_NOT_FOUND)

        otp = generate_otp(user)
        try:
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP for password reset is: {otp}",
                from_email="steveaustine126@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Reset password",
        operation_description="This endpoint resets the user's password using the OTP sent to their email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email"),
                "otp": openapi.Schema(type=openapi.TYPE_STRING, description="OTP sent to the user's email"),
                "new_password": openapi.Schema(type=openapi.TYPE_STRING, description="New password"),
                "confirm_password": openapi.Schema(type=openapi.TYPE_STRING, description="Confirm new password"),
            },
            required=["email", "otp", "new_password", "confirm_password"],
        ),
        responses={
            200: "Password reset successful.",
            400: "Invalid or expired OTP, or passwords do not match.",
            404: "User not found.",
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not all([email, otp, new_password, confirm_password]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        if user.otp != otp or user.otp_expiration < now():
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.otp = None
        user.otp_expiration = None
        user.save()

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)


class GenerateNewOTPView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Generate new OTP",
        operation_description="This endpoint generates a new OTP for email verification.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User's email"
                ),
            },
            required=["email"],
        ),
        responses={
            201: "Check your email for the OTP to verify your account.",
            400: "Invalid header found.",
            404: "User with this email does not exist or email is verified.",
            500: "Email sending failed.",
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email, is_verified=False)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist or email is verified."},
                status=status.HTTP_404_NOT_FOUND,
            )

        otp = generate_otp(user)
        try:
            send_mail(
                    subject="Verify Your Email",
                    message=f"Your OTP for email verification is: {otp}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                )
            return Response(
                {"message": "Check your email for the OTP to verify your account."},
                status=status.HTTP_201_CREATED
            )
        except BadHeaderError:
            return Response({"error": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Email sending failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Refresh access token",
        operation_description="This endpoint refreshes the access token using the refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="Refresh token to renew access token"),
            },
            required=["refresh"],
        ),
        responses={
            200: "Access token refreshed successfully.",
            400: "Invalid or expired refresh token.",
        },
    )
    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return Response({"access": str(access_token)}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({"error": "Invalid or expired refresh token."}, status=status.HTTP_400_BAD_REQUEST)
