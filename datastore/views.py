from django.http import Http404
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework import permissions
from datastore.authentication import TokenAuth
from datastore.models import ServiceUser, Data
from datastore.serializers import TokenSerializer, DataSerializer
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


class DataView(APIView):
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuth, )

    model = Data
    serializer_class = DataSerializer

    def get_throttles(self):
        """Set throttling scope 'main' to storing operations"""
        if self.request.method.lower() in ('put', 'post'):
            self.throttle_scope = 'main'
        return super().get_throttles()

    def get(self, request, slot_name=None):
        if not slot_name:
            query_set = self.model.objects.filter(service_user_id=request.auth)
            return Response(self.serializer_class(query_set, many=True).data)
        else:
            try:
                query_set = self.model.objects.get(
                    slot_name=slot_name,
                    service_user_id=request.auth
                )
            except self.model.DoesNotExist:
                raise Http404
            else:
                return Response(self.serializer_class(query_set).data)

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'token': request.auth},
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, slot_name):
        try:
            self.model.objects.get(
                slot_name=slot_name, service_user_id=request.auth).delete()
        except self.model.DoesNotExist:
            raise Http404
        else:
            return Response(status=HTTP_204_NO_CONTENT)

    def put(self, request, slot_name):
        try:
            instance = self.model.objects.get(
                service_user_id=request.auth,
                slot_name=slot_name
            )
        except self.model.DoesNotExist:
            raise Http404
        serializer = self.serializer_class(
            instance,
            data=request.data,
            partial=True
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            return Response(serializer.data)
