from rest_framework.authtoken.views import ObtainAuthToken
from datastore.models import ServiceUser
from datastore.serializers import TokenSerializer
from rest_framework.response import Response


class ObtainAuthTokenByService(ObtainAuthToken):
    serializer_class = TokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        service = serializer.validated_data['service']
        service_user_rel, _ = ServiceUser.objects.get_or_create(
            user=user, service=service)
        return Response({'token': service_user_rel.key})
