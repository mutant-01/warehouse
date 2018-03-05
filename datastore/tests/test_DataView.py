from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from datastore.models import Service, ServiceCategory, ServiceUser, Data
from datastore.views import DataView


class DataListViewTest(TestCase):

    test_username = "testUser"
    test_password = "testPass"
    service_unique_id = "unique"

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

    def setUp(self):
        self.factory = APIRequestFactory()

    def post_request_factory(self, data):
        request = self.factory.post('', data=data, format='json')
        force_authenticate(
            request,
            user=self.user,
            token=self.token
        )
        return request

    def test_post_empty(self):
        expected_json = {'json_data': None, 'slot_name': 'default'}
        request = self.post_request_factory(expected_json['json_data'])
        response = DataView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_resp = response.render().content
        self.assertJSONEqual(json_resp, expected_json)
        self.assertTrue(
            Data.objects.filter(service_user_id=self.token, slot_name='default').exists()
        )

    def test_post_data(self):
        expected_json = {'json_data': {'hi': 'bye'}, 'slot_name': 'some'}
        request = self.post_request_factory(expected_json)
        response = DataView.as_view()(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        json_resp = response.render().content
        self.assertJSONEqual(json_resp, expected_json)
        self.assertEqual(
            Data.objects.filter(json_data=expected_json['json_data']).count(),
            1
        )

    def create_resource(self, data):
        request = self.post_request_factory(data)
        DataView.as_view()(request)

    def get_request_factory(self):
        request = self.factory.get('test')
        force_authenticate(
            request,
            user=self.user,
            token=self.token
        )
        return request

    def test_get(self):
        expected_json_all = [
            {"json_data": {"hi": "hi"}, "slot_name": "shoot"},
            {"json_data": {"hi": "bye"}, "slot_name": "default"}
        ]
        expected_json_one = {"json_data": {"hi": "hi"}, "slot_name": "shoot"}
        self.create_resource({'json_data': {'hi': 'bye'}})
        self.create_resource({'json_data': {'hi': 'hi'}, 'slot_name': 'shoot'})
        # examine list all
        request = self.get_request_factory()
        response = DataView.as_view()(request)
        self.assertJSONEqual(response.render().content, expected_json_all)
        # examine get one
        request = self.get_request_factory()
        response = DataView.as_view()(request, slot_name=expected_json_one['slot_name'])
        self.assertJSONEqual(response.render().content, expected_json_one)

    def test_delete(self):
        self.create_resource({'json_data': {'hi': 'bye'}})
        self.create_resource({'json_data': {'hi': 'hi'}, 'slot_name': 'shoot'})
        request = self.factory.delete('test')
        force_authenticate(request, user=self.user, token=self.token)
        DataView.as_view()(request, 'shoot')
        with self.assertRaises(Data.DoesNotExist):
            Data.objects.get(service_user_id=self.token, slot_name='shoot')

    def test_put(self):
        expected_json = {'json_data': {'bye': 'bye'}, 'slot_name': 'shoot'}
        self.create_resource({'json_data': {'hi': 'hi'}, 'slot_name': 'shoot'})
        request = self.factory.put('test', data={'json_data': {'bye': 'bye'}}, format='json')
        force_authenticate(request, user=self.user, token=self.token)
        DataView.as_view()(request, 'shoot')
        self.assertTrue(
            Data.objects.filter(
                service_user_id=self.token, slot_name='shoot', json_data=expected_json['json_data']
            ).exists(),
        )
