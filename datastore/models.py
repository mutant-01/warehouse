import hashlib
import os
import binascii
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.db import models


class ServiceCategory(models.Model):
    name = models.CharField(max_length=1024, unique=True)
    available_instances = models.SmallIntegerField(null=True)


class Service(models.Model):
    unique_id = models.CharField(max_length=1024, unique=True)
    category = models.ForeignKey(ServiceCategory, models.CASCADE)


class ServiceUser(models.Model):
    """Model to hold service instance and user relationship,
     their data and auth token"""
    user = models.ForeignKey(User, models.CASCADE)
    service = models.ForeignKey(Service, models.CASCADE)
    # todo HashTable index is more efficient, as equal operator may be used more frequently
    key = models.CharField("token", max_length=40, primary_key=True)
    json_data = JSONField(null=True)
    # todo json_data index based on read/write frequency

    class Meta:
        unique_together = (('user', 'service'), )

    def save(self, *args, **kwargs):
        """Saves calculated auth token per instance"""
        if not self.key:
            self.key = self._generate_key()
        return super().save(*args, **kwargs)

    def _generate_key(self):
        """Generates auth token based on username, service id and randomness"""
        d = hashlib.sha1()
        random = binascii.hexlify(os.urandom(20)).decode()
        user = self.user.username
        service = self.service.unique_id
        d.update((random + user + service).encode())
        return d.hexdigest()
