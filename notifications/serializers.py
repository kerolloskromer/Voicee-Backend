from rest_framework import serializers

from .models import FCMDeviceToken


class FCMDeviceTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = FCMDeviceToken
        fields = ('token',)