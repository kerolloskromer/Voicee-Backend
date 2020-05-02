from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from firebase_admin import credentials, initialize_app

from .base_authentication import BaseFirebaseAuthentication

firebase_creds = credentials.Certificate(settings.FIREBASE_KEY)
firebase_app = initialize_app(firebase_creds)


class FirebaseAuthentication(BaseFirebaseAuthentication):
    """
    Example implementation of a DRF Firebase Authentication backend class
    """

    def get_firebase_app(self):
        return firebase_app

    def get_django_user(self, firebase_user_record):

        user = get_user_model().objects.get_or_create(
            username = firebase_user_record.phone_number,
            firebase_uid = firebase_user_record.uid,
            phone_number = firebase_user_record.phone_number,
            # display_name = firebase_user_record.dis,
            # email = firebase_user_record.email,
            # email_verified = firebase_user_record.email_verified,
            # photo_url = firebase_user_record.photo_url,
            # disabled = firebase_user_record.disabled,
        )[0]

        update_last_login(None, user)            

        return user
