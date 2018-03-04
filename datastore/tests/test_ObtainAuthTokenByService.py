from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from datastore.models import Service, ServiceUser
from datastore.models import ServiceCategory
from datastore.views import ObtainAuthTokenByService
from rest_framework import status


class ObtainAuthTokenByServiceTest(TestCase):

    test_username = "testUser"
    test_password = "testPass"
    service_unique_id = "unique"

    def setUp(self):
        self.factory = APIRequestFactory()
        self.test_view = ObtainAuthTokenByService.as_view()

    @classmethod
    def setUpTestData(cls):
        cls.category = ServiceCategory.objects.create(
            name="cat1", available_instances=2)
        cls.service = Service.objects.create(
            unique_id=cls.service_unique_id, category=cls.category)
        cls.user = User.objects.create_user(
            cls.test_username, password=cls.test_password)

    def test_token(self):
        request = self.factory.post(
            "shoot",
            format='json',
            data={
                'username': self.test_username,
                'password': self.test_password,
                'service_unique_id': self.service_unique_id
            }
        )
        response = self.test_view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ServiceUser.objects.filter(key=response.render().data['token']).count(),
            1
        )
