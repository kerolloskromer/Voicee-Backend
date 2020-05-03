from django.contrib import admin

from .models import FCMDeviceToken, Notification


class DeviceTokenAdmin(admin.ModelAdmin):
    date_hierarchy = 'updated_at'
    list_display = ('token', 'user', 'active', 'created_at', 'updated_at',)
    actions = ['send_test_notification']
    list_filter = ('active',)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.method == 'GET'

    def save_model(self, request, obj, form, change):
        if request.user.is_superuser:
            return super(DeviceTokenAdmin, self).save_model(
                request, obj, form, change)

    def delete_model(self, request, obj, form, change):
        if request.user.is_superuser:
            return super(DeviceTokenAdmin, self).save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        if request.user.is_superuser:
            return super(DeviceTokenAdmin, self).save_related(
                request, form, formsets, change)

    def get_actions(self, request):
        actions = super(DeviceTokenAdmin, self).get_actions(request)
        if not request.user.is_superuser:
            del actions['delete_selected']
        return actions

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ['token', 'user', 'active']
        return []

    def send_test_notification(self, request, queryset):
        title = 'Test notification'
        body = FCMDeviceToken.construct_body(
            title, 'test', 'This is a test notification', None)
        for token in queryset:
            token.send_notification(body)
        notification = Notification()
        notification.text = title
        notification.save()
    send_test_notification.short_description = "Send test notification"

admin.site.register(FCMDeviceToken,DeviceTokenAdmin)
admin.site.register(Notification)
