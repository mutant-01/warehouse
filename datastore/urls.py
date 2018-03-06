from django.urls import path
from datastore.views import DataView, ObtainAuthTokenByService

app_name = 'datastore'

urlpatterns = [
    path('data', DataView.as_view()),
    path('auth', ObtainAuthTokenByService.as_view()),
]
