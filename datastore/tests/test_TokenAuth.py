from django.test import TestCase
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User
from datastore.authentication import TokenAuth
from datastore.models import ServiceCategory, Service, ServiceUser


class TokenSerializerTest(TestCase):

    test_username = "testUser"
    test_password = "testPass"
    service_unique_id = "unique"

    def setUp(self):
        self.factory = APIRequestFactory()

    @classmethod
    def setUpTestData(cls):
        cls.category = ServiceCategory.objects.create(
            name="cat1", available_instances=2)
        cls.service = Service.objects.create(
            unique_id=cls.service_unique_id, category=cls.category)
        cls.user = User.objects.create_user(
            cls.test_username, password=cls.test_password)
        cls.token = ServiceUser.objects.create(
            service=cls.service,
            user=cls.user
        ).key

    def test_authentication(self):
        request = self.factory.get(
            "test",
            HTTP_AUTHORIZATION='token ' + self.token
        )
        user, token = TokenAuth().authenticate(request)
        self.assertEqual(user, self.user)
        self.assertEqual(token, self.token)
