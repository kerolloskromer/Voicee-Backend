from rest_framework import serializers

from .models import FCMDeviceToken, Notification


class FCMDeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDeviceToken
        fields = ('token',)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"
