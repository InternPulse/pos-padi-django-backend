from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Company
from apps.users.models import User

class CompanyEndpointsTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user without an associated company for create tests
        cls.test_user_no_company = User.objects.create_user(
            email="nocompany@example.com",
            password="StrongPassword123!",
            first_name="NoCompany",
            last_name="User",
            role="owner",
            phone="0987654321",
            nin="98765432101"
        )

        # Create a test user with an associated company for other tests
        cls.test_user = User.objects.create_user(
            email="testowner@example.com",
            password="StrongPassword123!",
            first_name="Test",
            last_name="Owner",
            role="owner",
            phone="1234567890",
            nin="12345678901"
        )

        cls.test_company = Company.objects.create(
            owner=cls.test_user,
            name="Test Company",
            state="Test State",
            lga="Test LGA",
            area="Test Area"
        )

    def setUp(self):
        self.client.force_authenticate(user=self.test_user)
        self.company_url = reverse('api:company-list', kwargs={'version': 'v1'})
        self.company_detail_url = reverse('api:company-detail', kwargs={'version': 'v1', 'pk': self.test_company.pk})

    def test_list_companies(self):
        response = self.client.get(self.company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_retrieve_company(self):
        response = self.client.get(self.company_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.test_company.name)

    def test_create_company(self):
        self.client.force_authenticate(user=self.test_user_no_company)
        data = {
            "name": "New Company",
            "state": "New State",
            "lga": "New LGA",
            "area": "New Area",
            "address": "123 Test Address"
        }

        response = self.client.post(self.company_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], data["name"])

    def test_delete_company(self):
        response = self.client.delete(self.company_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_company(self):
        data = {"state": "Updated State"}
        response = self.client.patch(self.company_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["state"], data["state"])
