from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^notifications/fcm/?$',
        view=views.RegisterFCM.as_view(),
        name='register-fcm'
    ),
    url(
        regex=r'^notifications/fcm/deregister?$',
        view=views.DeregisterFCM.as_view(),
        name='deregister-fcm'
    ),
]