# apps/users/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, JSONParser
from django.core.mail import send_mail,BadHeaderError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import  AllowAny
import random
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.exceptions import ValidationError

from .serializers import RegistrationSerializer, LoginSerializer
from .tokens import email_verification_token
from .models import User

class RegistrationAPIView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
         # Optional: capture the version if you need it

        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate OTP for email verification
            otp = self.generate_otp(user)

            try:
                send_mail(
                    subject="Verify Your Email",
                    message=f"Your OTP for email verification is: {otp}",
                    from_email="steveaustine126@gmail.com",
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return Response(
                    {"message": "User registered successfully. Check your email for the OTP to verify your account."},
                    status=status.HTTP_201_CREATED
                )
            except BadHeaderError:
                return Response({"error": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Email sending failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_otp(self, user):
        otp = random.randint(100000, 999999)
        user.otp = otp
        user.otp_expiration = now() + timedelta(seconds=59)
        user.save()
        return otp

class LoginAPIView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [AllowAny]
    
    def post(self, request, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class VerifyEmailAPIView(APIView):
    permission_classes = [AllowAny]

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

    def generate_otp(self, user):
        otp = random.randint(100000, 999999)
        user.otp = otp
        user.otp_expiration = now() + timedelta(seconds=59)
        user.save()
        return otp