from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIRequestFactory
from datastore.models import Service, ServiceCategory
from datastore.serializers import TokenSerializer


class TokenSerializerTest(TestCase):

    test_username = "testUser"
    test_password = "testPass"
    service_unique_id = "unique"

    def setUp(self):
        self.request = APIRequestFactory().post(
            "test",
            format='json'
        )

    @classmethod
    def setUpTestData(cls):
        cls.category = ServiceCategory.objects.create(
            name="cat1", available_instances=2)
        cls.service = Service.objects.create(
            unique_id=cls.service_unique_id, category=cls.category)
        cls.user = User.objects.create_user(
            cls.test_username, password=cls.test_password)

    def test_user_service_validation(self):
        data = {
            'username': self.test_username,
            'password': self.test_password,
            'service_unique_id': self.service_unique_id
        }
        serializer = TokenSerializer(
            data=data, context={'request': self.request})
        self.assertTrue(serializer.is_valid())

    def test_user_service_data_length(self):
        data = {
            'username': 'a'*151,
            'password': 'a'*129,
            'service_unique_id': self.service_unique_id
        }
        serializer = TokenSerializer(
            data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())

    def test_invalid_service_id(self):
        data = {
            'username': self.test_username,
            'password': self.test_password,
            'service_unique_id': "shoot"
        }
        serializer = TokenSerializer(
            data=data, context={'request': self.request})
        self.assertFalse(serializer.is_valid())
