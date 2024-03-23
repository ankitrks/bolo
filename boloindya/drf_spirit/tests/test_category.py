from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from .utils import CategoryFactory


class CategoryTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.username = 'testadmin'
        self.email = 'testadmin@testing.com'
        self.password = 'testpass'
        self.user = User.objects.create_user(
            self.username, self.email, self.password
        )

    def test_get(self):
        # creating few categories
        CategoryFactory(size=3)

        response = self.client.get(reverse('drf_spirit:category-list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
