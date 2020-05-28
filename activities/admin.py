from django.contrib import admin
from .models import Action, Notification


class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'verb', 'target', 'date')
    list_filter = ('date',)
    search_fields = ('verb',)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user',)

admin.site.register(Action, ActionAdmin)
admin.site.register(Notification, NotificationAdmin)