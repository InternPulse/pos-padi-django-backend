from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Customer
from apps.users.models import User
from apps.agents.models import Agent
from apps.companies.models import Company

class CustomerEndpointsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user and agent
        cls.test_user = User.objects.create_user(
            email="testagent@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="Agent",
            phone="1234567890",
            nin="12345678901",
            role="agent",
            is_verified=True
        )

        # Create a test owner
        cls.test_owner = User.objects.create_user(
            email="testowner@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="Owner",
            phone="0987654321",
            nin="10987654321",
            role="owner",
            is_verified=True
        )

        # Create a test company
        cls.test_company = Company.objects.create(
            owner=cls.test_owner,  # Assign the owner to the company
            name="Test Company",
            address="123 Test Street",
            registration_number="123456789"
        )

        cls.test_agent = Agent.objects.create(
            user_id=cls.test_user,
            company=cls.test_company,  # Associate the agent with the test company
            commission=0.1,
            rating=5.0,
            status="active"
        )

        # Create a test customer
        cls.test_customer = Customer.objects.create(
            user=cls.test_user,
            name="Test Customer",
            customer_id="123456"
        )

    def setUp(self):
        login_url = reverse('api:login', kwargs={'version': 'v1'})
        login_data = {
            "email": "testagent@example.com",
            "password": "StrongPassword123!"
        }
        response = self.client.post(login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

        self.customer_url = reverse('api:customer-list', kwargs={'version': 'v1'})
        self.customer_detail_url = reverse('api:customer-detail', kwargs={'version': 'v1', 'pk': self.test_customer.pk})
        self.customer_transactions_url = reverse('api:customer-transactions', kwargs={'version': 'v1', 'pk': self.test_customer.pk})
        self.customer_transaction_summary_url = reverse('api:customer-transaction-summary', kwargs={'version': 'v1', 'pk': self.test_customer.pk})

    def test_list_customers(self):
        response = self.client.get(self.customer_url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_retrieve_customer(self):
        response = self.client.get(self.customer_detail_url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_customer_transactions(self):
        response = self.client.get(self.customer_transactions_url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])

    def test_customer_transaction_summary(self):
        response = self.client.get(self.customer_transaction_summary_url)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
