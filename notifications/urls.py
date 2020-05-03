from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^notifications/register/?$',
        view=views.RegisterFCM.as_view(),
        name='register-fcm'
    ),
    url(
        regex=r'^notifications/?$',
        view=views.NotificationListView.as_view(),
        name='notifications-list'
    ),
]