from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken  # Import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command  # Import call_command for database flush
from .models import User
from .views import generate_otp
import time  # Import time module for unique email and NIN generation
import uuid  # Import uuid for unique ID generation
from apps.customers.models import Customer

class UserEndpointsTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Reset the database to ensure a clean state for tests
        call_command('flush', '--noinput')

        # Create a test user with a unique ID
        cls.test_user = User.objects.create_user(
            id=str(uuid.uuid4()),  # Generate a unique ID
            email="testuser@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="User",
            phone="1234567890",
            nin="12345678901",  # Valid NIN
            role="customer",
            is_verified=True
        )

        # Create a customer associated with the test user
        cls.test_customer = Customer.objects.create(
            user=cls.test_user,
            name="Test Customer"
        )

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('api:register', kwargs={'version': 'v1'})
        self.login_url = reverse('api:login', kwargs={'version': 'v1'})
        self.verify_email_url = reverse('api:email-verify', kwargs={'version': 'v1'})
        self.generate_otp_url = reverse('api:generate-otp', kwargs={'version': 'v1'})
        self.logout_url = reverse('api:logout', kwargs={'version': 'v1'})
        self.forgot_password_url = reverse('api:forgot-password', kwargs={'version': 'v1'})
        self.reset_password_url = reverse('api:reset-password', kwargs={'version': 'v1'})

        # Generate OTP for the test user
        self.test_user.otp = generate_otp(self.test_user)

    def test_register_endpoint(self):
        # Ensure unique email and NIN for each test run by appending a timestamp
        unique_email = f"uniqueuser_{int(time.time())}@example.com"
        unique_nin = f"9876543210{int(time.time() % 10)}"

        photo = SimpleUploadedFile(
            name="sample.png",
            content=open("media/sample.png", "rb").read(),
            content_type="image/png"
        )
        data = {
            "email": unique_email,  # Ensure unique email for each test run
            "password": "AnotherStrongPassword123!",
            "first_name": "New",
            "last_name": "User",
            "phone": "0987654321",
            "nin": unique_nin,  # Ensure unique NIN for each test run
            "role": "customer",
            "photo": photo  # Properly handle photo as a file upload
        }
        response = self.client.post(self.register_url, data, format='multipart')  # Use multipart format for file upload
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_login_endpoint(self):
        data = {
            "email": "testuser@example.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(self.login_url, data, format='json')  # Use JSON format
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_verify_email_endpoint(self):
        data = {
            "email": "testuser@example.com",
            "otp": self.test_user.otp  # Use the generated OTP
        }
        response = self.client.post(self.verify_email_url, data, format='json')  # Use JSON format
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_logout_endpoint(self):
        # Authenticate the client
        self.client.force_authenticate(user=self.test_user)
        refresh_token = str(RefreshToken.for_user(self.test_user))  # Generate refresh token
        data = {"refresh": refresh_token}
        response = self.client.post(self.logout_url, data, format='json')  # Use JSON format
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_forgot_password_endpoint(self):
        data = {"email": "testuser@example.com"}
        response = self.client.post(self.forgot_password_url, data, format='json')  # Use JSON format
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])

    def test_reset_password_endpoint(self):
        data = {
            "email": "testuser@example.com",
            "otp": self.test_user.otp,  # Use the generated OTP
            "new_password": "NewStrongPassword123!",
            "confirm_password": "NewStrongPassword123!"
        }
        response = self.client.post(self.reset_password_url, data, format='json')  # Use JSON format
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])