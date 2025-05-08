# apps/users/views.py
import random
from datetime import timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.core.mail import send_mail, BadHeaderError
from django.utils.timezone import now
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .models import User
from .serializers import RegistrationSerializer, LoginSerializer
from ..customers.serializers import CustomerSerializer, Customer
from ..agents.serializers import AgentSerializer, Agent
from ..companies.serializers import CompanySerializer, Company
from ..external_tables.serializers import (
    TransactionSerializer,
    Transaction,
    Notification,
    NotificationSerializer,
)


def generate_otp(user):
    otp = random.randint(100000, 999999)
    user.otp = otp
    user.otp_expiration = now() + timedelta(seconds=300)
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
            user.role = "owner"  # Default role
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
                    {
                        "message": "User registered successfully. Check your email for the OTP to verify your account."
                    },
                    status=status.HTTP_201_CREATED,
                )
            except Exception as e:
                return Response(
                    {"error": f"An error occurred while processing your request. {e}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
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
                "role": user.role,
                "full_name": f"{user.first_name} {user.last_name}",
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
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User's email"
                ),
                "otp": openapi.Schema(
                    type=openapi.TYPE_STRING, description="OTP sent to the user's email"
                ),
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
            return Response(
                {"error": "OTP and email are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if user.otp != otp or user.otp_expiration < now():
            return Response(
                {"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST
            )

        user.is_verified = True
        user.otp = None
        user.otp_expiration = None
        user.save()

        return Response(
            {"message": "Email verified successfully."}, status=status.HTTP_200_OK
        )


class LogoutAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Logout user",
        operation_description="This endpoint logs out a user by blacklisting their refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Refresh token to blacklist"
                ),
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
                return Response(
                    {"error": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {"message": "Logout successful."}, status=status.HTTP_200_OK
            )
        except TokenError:
            return Response(
                {"error": "Invalid or expired token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Forgot password",
        operation_description="This endpoint sends an OTP to the user's email for password reset.",
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
            200: "OTP sent to your email.",
            404: "User with this email does not exist or is not verified.",
            500: "Failed to send email.",
        },
    )
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email, is_verified=True)
        except User.DoesNotExist:
            return Response(
                {"error": "User with this email does not exist or is not verified."},
                status=status.HTTP_404_NOT_FOUND,
            )

        otp = generate_otp(user)
        try:
            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP for password reset is: {otp}",
                from_email="steveaustine126@gmail.com",
                recipient_list=[user.email],
                fail_silently=False,
            )
            return Response(
                {"message": "OTP sent to your email."}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Reset password",
        operation_description="This endpoint resets the user's password using the OTP sent to their email.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, description="User's email"
                ),
                "otp": openapi.Schema(
                    type=openapi.TYPE_STRING, description="OTP sent to the user's email"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New password"
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Confirm new password"
                ),
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
            return Response(
                {"error": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if user.otp != otp or user.otp_expiration < now():
            return Response(
                {"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.otp = None
        user.otp_expiration = None
        user.save()

        return Response(
            {"message": "Password reset successful."}, status=status.HTTP_200_OK
        )


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
                status=status.HTTP_201_CREATED,
            )
        except BadHeaderError:
            return Response(
                {"error": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": f"Email sending failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RefreshTokenAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Refresh access token",
        operation_description="This endpoint refreshes the access token using the refresh token.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Refresh token to renew access token",
                ),
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
            return Response(
                {"error": "Refresh token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            return Response({"access": str(access_token)}, status=status.HTTP_200_OK)
        except TokenError:
            return Response(
                {"error": "Invalid or expired refresh token."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Get user summary",
        operation_description="This endpoint retrieves a summary of the user's data, including associated companies, agents, transactions, and customers based on the user's role.",
        responses={
            200: "User summary retrieved successfully.",
            403: "Authentication credentials were not provided or invalid.",
        },
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        if user.role == "owner":
            user_data = RegistrationSerializer(user).data
            company_data = CompanySerializer(Company.objects.filter(owner=user), many=True).data
            agents = AgentSerializer(
                Agent.objects.filter(company__owner=user), many=True
            ).data
            agent_ids = [agent["agent_id"] for agent in agents]
            transactions = Transaction.objects.filter(agent_id__in=agent_ids)
            transactions_data = TransactionSerializer(transactions, many=True).data
            notifications_data = NotificationSerializer(
                Notification.objects.filter(user_id=user.id), many=True
            ).data
            customer_ids = transactions.values_list("customer_id", flat=True).distinct()
            customers_data = CustomerSerializer(
                Customer.objects.filter(id__in=customer_ids), many=True
            ).data

            data = {
                "user": user_data,
                "company": company_data,
                "agents": agents,
                "transactions": transactions_data,
                "customers": customers_data,
                "notifications": notifications_data
            }

        elif user.role == "agent":
            user_data = AgentSerializer(user.agent).data
            agent_id = user.agent.agent_id
            transactions = Transaction.objects.filter(agent_id=agent_id)
            company_data = CompanySerializer(user.agent.company).data
            transactions_data = TransactionSerializer(transactions, many=True).data
            notifications_data = NotificationSerializer(
                Notification.objects.filter(user_id=user.id), many=True
            ).data
            customer_ids = transactions.values_list("customer_id", flat=True).distinct()
            customers_data = CustomerSerializer(
                Customer.objects.filter(id__in=customer_ids), many=True
            ).data

            data = {
                "user": user_data,
                "company": company_data,
                "transactions": transactions_data,
                "customers_data": customers_data,
                "notifications": notifications_data,
            }


        elif user.role == "customer":
            user_data = CustomerSerializer(Customer.objects.get(user=user)).data
            transactions = Transaction.objects.filter(customer_id__user=user)
            transactions_data = TransactionSerializer(transactions, many=True).data
            notifications_data = NotificationSerializer(
                Notification.objects.filter(user_id=user), many=True
            ).data

            data = {
                "user": user_data,
                "notifications": notifications_data,
                "transactions": transactions_data,
            }

        return Response(data)


class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Change password",
        operation_description="This endpoint allows an authenticated user to change their password by providing the current password, a new password, and confirming the new password.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "current_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Current password"
                ),
                "new_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="New password"
                ),
                "confirm_password": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Confirm new password"
                ),
            },
            required=["current_password", "new_password", "confirm_password"],
        ),
        responses={
            200: "Password changed successfully.",
            400: "Invalid current password or passwords do not match.",
        },
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not all([current_password, new_password, confirm_password]):
            return Response(
                {"error": "All fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if new_password != confirm_password:
            return Response(
                {"error": "New passwords do not match."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )

class EmailToggleSettingButton(APIView):
    permission_classes = [IsAuthenticated]

    # a patch request to check the toggel key value set by the user on the frontend
    @swagger_auto_schema(
        operation_summary="Toggle email setting",
        operation_description="This endpoint allows a user to toggle their email setting.",
        responses={
            200: "Email settings updated successfully.",
        },
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        user.is_email_enabled = not user.is_email_enabled  # Toggle the status
        user.save()

        return Response(
            {"message": "email toggle settings updated successfully."},
            status=status.HTTP_200_OK,
        )
    
class PushNotificationSettingButton(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Toggle push notification setting",
        operation_description="This endpoint allows a user to toggle their push notification settings.",
        responses={
            200: "Push notification settings updated successfully.",
        },
    )
    def patch(self, request, *args, **kwargs):
        user = request.user
        user.is_push_notification_enabled = not user.is_push_notification_enabled  # Toggle the status
        user.save()

        return Response(
            {"message": "Push notification settings updated successfully."},
            status=status.HTTP_200_OK,
        )