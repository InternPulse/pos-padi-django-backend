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
from rest_framework.permissions import AllowAny



from .serializers import RegistrationSerializer, LoginSerializer
from .tokens import email_verification_token
from .models import User

class RegistrationAPIView(APIView):
    parser_classes = [MultiPartParser, JSONParser]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate email verification token
            token = email_verification_token.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_url = f"{request.scheme}://{request.get_host()}/api/v1/verify/{uid}/{token}/"

            try:
                send_mail(
                    subject="Verify Your Email",
                    message=f"Click the link to verify your email: {verification_url}",
                    from_email="noreply@example.com",  # Replace with your configured email
                    recipient_list=[user.email],
                    fail_silently=False,
                )
                return Response(
                    {"message": "User registered successfully. Check your email to verify your account."},
                    status=status.HTTP_201_CREATED
                )
            except BadHeaderError:
                return Response({"error": "Invalid header found."}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({"error": f"Email sending failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class LoginAPIView(APIView):
    def post(self, request):
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
    permission_classes = [AllowAny]  # Allow unauthenticated access

    @swagger_auto_schema(
        responses={
            200: openapi.Response(
                description="Email verified successfully.",
            ),
            400: openapi.Response(
                description="Invalid verification link.",
            ),
        },
    )
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and email_verification_token.check_token(user, token):
            user.is_verified = True
            user.is_active = True  # Activate the user after email verification
            user.save()
            return Response({"message": "Email verified successfully."})
        return Response({"error": "Invalid verification link."}, status=status.HTTP_400_BAD_REQUEST)

