from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from datastore.models import ServiceUser


class TokenAuth(BaseAuthentication):
    keyword = 'token'
    model = ServiceUser

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            raise AuthenticationFailed(
                'Invalid token header. No credentials provided.')
        elif len(auth) > 2:
            raise AuthenticationFailed(
                'Invalid token header. Token string should not contain spaces.')

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise AuthenticationFailed(
                'Invalid token header. Token string should not contain invalid characters.')

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        try:
            service_user = self.model.objects.get(key=token)
        except self.model.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
        else:
            if not service_user.user.is_active:
                raise AuthenticationFailed('User inactive or deleted.')
            return service_user.user, service_user.key

    def authenticate_header(self, request):
        return self.keyword
