from django.contrib.auth.models import User
from django.test import TestCase
from datastore.models import ServiceCategory, Service, ServiceUser, Data, DataLog


class test_Data_log(TestCase):

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

    def create_data(self, count=1):
        for i in range(count):
            Data.objects.create(
                slot_name=str(i),
                service_user_id=self.token,
                json_data={str(i): str(i)}
            )

    def test_create(self):
        self.create_data(count=5)
        self.assertEqual(
            DataLog.objects.all().count(), 5
        )

    def test_update(self):
        self.create_data(count=1)
        d = Data.objects.get()
        d.slot_name = "shoot"
        d.save()
        self.assertEqual(
            DataLog.objects.all().count(), 2
        )

    def test_delete(self):
        self.create_data(count=1)
        d = Data.objects.get()
        d.delete()
        self.assertEqual(
            DataLog.objects.all().count(), 2
        )
