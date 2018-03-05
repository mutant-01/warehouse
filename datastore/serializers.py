from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from datastore.models import Service, Data


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128)
    service_unique_id = serializers.CharField(max_length=1024)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        service_unique_id = attrs.get('service_unique_id')
        if service_unique_id:
            try:
                service = Service.objects.get(unique_id=service_unique_id)
            except Service.DoesNotExist:
                raise serializers.ValidationError(
                    "not valid service unique id", code='authorization')
        else:
            raise serializers.ValidationError(
                "must include service_unique_id",
                code='authorization')

        if username and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        attrs['service'] = service
        return attrs

    def create(self, validated_data):
        raise NotImplemented

    def update(self, instance, validated_data):
        raise NotImplemented


class DataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Data
        fields = ('json_data', 'slot_name')

    def create(self, validated_data):
        token = self.context['token']
        return self.Meta.model.objects.create(service_user_id=token, **validated_data)

    def update(self, instance, validated_data):
        instance.json_data = validated_data['json_data']
        instance.save()
        return instance
