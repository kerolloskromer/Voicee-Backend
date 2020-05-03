from django.db import IntegrityError
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated

from .models import FCMDeviceToken
from .serializers import FCMDeviceTokenSerializer


class RegisterFCM(CreateAPIView, UpdateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = FCMDeviceTokenSerializer

    def get_object(self):
        return FCMDeviceToken.objects.get(
            token__iexact=self.request.data.get('token'))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, active=True)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user, active=True)

    def create(self, request, *args, **kwargs):
        token = request.data.get('token', None)
        if token and FCMDeviceToken.objects.filter(
                token__iexact=token).exists():
            return self.update(self.request, *args, **kwargs)
        try:
            return super(RegisterFCM, self).create(request, *args, **kwargs)
        except IntegrityError:
            return self.update(self.request, *args, **kwargs)


class DeregisterFCM(UpdateAPIView):
    serializer_class = FCMDeviceTokenSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return FCMDeviceToken.objects.get(
            token__iexact=self.request.data.get('token'))

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
