from __future__ import print_function, unicode_literals

import json
import logging
from datetime import datetime, timedelta
from typing import Sequence

import firebase_admin
from django.conf import settings
from django.db import models
from firebase_admin import messaging
from firebase_admin.exceptions import FirebaseError

logger = logging.getLogger(__name__)

FIVE_MINUTES = timedelta(minutes=5)

DEFAULT_VIBRATION_PATTERN =  [200, 100, 200, 100, 200, 100, 200]


ANDROID_PRIORITIES = {
    'very-low': 'normal',
    'low': 'normal',
    'normal': 'normal',
    'high': 'high',
}

IOS_PRIORITIES = {
    'very-low': '5',
    'low': '5',
    'normal': '10',
    'high': '10',
}


class FCMDeviceToken(models.Model):
    # Provided by App
    token = models.CharField(max_length=255, unique=True)

    # Done by the server
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='fcm_devices',
        null=True, on_delete=models.SET_NULL)
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(
            self.user,
            'Active' if self.active else 'Inactive')

    @staticmethod
    def construct_body(title: str, topic: str, category: str = None,
                       data: dict = None, body_text: str = '',
                       alert_sound: str = 'default', critical: bool = False,
                       web_badge: str = '', web_icon: str = '',
                       vibration_pattern: Sequence[int] = None,
                       priority: str = 'normal'):
        if data is None:
            data = {}
        if vibration_pattern is None:
            vibration_pattern = DEFAULT_VIBRATION_PATTERN

        android_notification_additional_config = {}
        aps_additional_config = {}

        if category is not None:
            android_notification_additional_config['click_action'] = category
            aps_additional_config['category'] = category

        # https://developer.apple.com/library/archive/documentation/NetworkingInternet/Conceptual/RemoteNotificationsPG/PayloadKeyReference.html#//apple_ref/doc/uid/TP40008194-CH17-SW5
        fcm_body = {
            'data': data,
            'android': messaging.AndroidConfig(
                priority=ANDROID_PRIORITIES[priority],  # normal and high
                ttl=300,
                notification=messaging.AndroidNotification(
                    title=title,
                    body=body_text,
                    **android_notification_additional_config,
                ),
            ),
            'webpush': messaging.WebpushConfig(
                headers={
                    'TTL': '300',
                    'Urgency': priority,  # can be very-low, low, normal, or high
                    'Topic': topic,
                },
                # Send everything in a dict instead so that we can handle the notifications ourselves.
                data=dict(
                    notification=json.dumps(dict(
                        title=title,
                        body=body_text,
                        # URL for badge icon
                        badge=web_badge,
                        icon=web_icon,  # URL for icon
                        # should the user be renotified if an old notification is replaced by a new one
                        # renotify=True,
                        # Should the notification remain active until the user clicks or dismisses it rather than closing automatically
                        require_interaction=False,
                        silent=False,  # should the notification be comletely silent regardless of device settings
                        # vibration pattern
                        vibrate=vibration_pattern,
                    )),
                    **data
                ),
                # fcm_options=messaging.WebpushFcmOptions(
                #     link='',  # link to open when the user clicks on the notification
                # ),
            ),
            'apns': messaging.APNSConfig(
                headers={
                    # The date at which the notification is no longer valid. This value
                    # is a Unix epoch expressed in seconds (UTC). If the value is
                    # nonzero, APNs stores the notification and tries to deliver it at
                    # least once, repeating the attempt as needed until the specified
                    # date. If the value is 0, APNs attempts to deliver the
                    # notification only once and does not store the notification.
                    'apns-expiration': str(int(datetime.timestamp(
                        datetime.utcnow() + FIVE_MINUTES))),

                    # This should be the default, but we will specify it here manually.
                    # 10 should be immediate, while 5 does it based off of power
                    # considerations.
                    'apns-priority': IOS_PRIORITIES[priority],

                    # Generally the app's bundle ID.
                    # 'apns-topic': settings.FCM_NOTIFICATIONS['bundle_id'],

                    # 64 bytes at most and is used to collapse notifications if the
                    # notifications are the same.
                    'apns-collpase-id': topic,
                },
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        alert=messaging.ApsAlert(
                            title=title,  # short string that descirbes purpose
                            # subtitle='',
                            body=body_text,  # body text of message
                        ),
                        # badge=0,  # badge counter
                        sound=messaging.CriticalSound(
                            alert_sound, critical=critical, volume=1),  # sound to play
                        content_available=True,  # use 1 to indicate that the system has new data to handle

                        # used for grouping along with a Notification Content app extension
                        mutable_content=True,
                        custom_data=data,
                        **aps_additional_config,
                    ),
                    **data
                ),
            ),
        }

        return fcm_body

    def send_notification(self, body, *args):
        try:
            message = messaging.Message(
                token=self.token,
                **body
            )
            response = messaging.send(message)
        except FirebaseError as fbe:
            # https://firebase.google.com/docs/cloud-messaging/send-message#admin_sdk_error_reference
            if fbe.code in [
                'messaging/invalid-recipient',
                'messaging/invalid-registration-token',
                'messaging/registration-token-not-registered',
            ]:
                self.active = False
                self.save()
            else:
                self.active = False
                self.save()
                logger.exception(
                    'Failed to send notification from FCM',
                    extra={
                        'user': self.user,
                        'data': json.dumps(body.get('data', ''))
                    },
                )
        except Exception as e:
            logger.exception('Failed to send notification', extra={
                'user': self.user,
                'data': json.dumps(body.get('data', ''))
            })
