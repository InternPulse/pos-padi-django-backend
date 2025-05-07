import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from apps.users.models import User
from datetime import timedelta
from django.utils.timezone import now

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user():
    def _create_user(**kwargs):
        return User.objects.create_user(**kwargs)
    return _create_user

@pytest.mark.django_db
def test_register_user(api_client):
    url = reverse('api:register', kwargs={"version": "v1"})
    data = {
        "email": "testuser@example.com",
        "first_name": "Test",
        "last_name": "User",
        "phone": "1234567890",
        "nin": "12345678901",
        "password": "StrongPassword123!"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert "message" in response.data

@pytest.mark.django_db
def test_login_user(api_client, create_user):
    user = create_user(
        email="testuser@example.com",
        password="StrongPassword123!",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        nin="12345678901",
        role="owner",
        is_verified=True
    )
    url = reverse('api:login', kwargs={"version": "v1"})
    data = {
        "email": user.email,
        "password": "StrongPassword123!"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data
    assert "refresh" in response.data

@pytest.mark.django_db
def test_verify_email(api_client, create_user):
    user = create_user(
        email="testuser@example.com",
        password="StrongPassword123!",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        nin="12345678901",
        role="owner",
        otp="123456",
        otp_expiration=now() + timedelta(minutes=5)
    )
    url = reverse('api:email-verify', kwargs={"version": "v1"})
    data = {
        "email": user.email,
        "otp": "123456"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.data

@pytest.mark.django_db
def test_forgot_password(api_client, create_user):
    user = create_user(
        email="testuser@example.com",
        password="StrongPassword123!",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        nin="12345678901",
        role="owner",
        is_verified=True
    )
    url = reverse('api:forgot-password', kwargs={"version": "v1"})
    data = {"email": user.email}
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.data

@pytest.mark.django_db
def test_reset_password(api_client, create_user):
    user = create_user(
        email="testuser@example.com",
        password="StrongPassword123!",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        nin="12345678901",
        role="owner",
        otp="123456",
        otp_expiration=now() + timedelta(minutes=5)
    )
    url = reverse('api:reset-password', kwargs={"version": "v1"})
    data = {
        "email": user.email,
        "otp": "123456",
        "new_password": "NewStrongPassword123!",
        "confirm_password": "NewStrongPassword123!"
    }
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.data

@pytest.mark.django_db
def test_logout_user(api_client, create_user):
    user = create_user(
        email="testuser@example.com",
        password="StrongPassword123!",
        first_name="Test",
        last_name="User",
        phone="1234567890",
        nin="12345678901",
        role="owner",
        is_verified=True
    )
    url = reverse('api:login', kwargs={"version": "v1"})
    data = {
        "email": user.email,
        "password": "StrongPassword123!"
    }
    login_response = api_client.post(url, data, format='json')
    refresh_token = login_response.data["refresh"]

    url = reverse('api:logout', kwargs={"version": "v1"})
    data = {"refresh": refresh_token}
    response = api_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.data