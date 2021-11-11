from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.chats.admin import MembershipInline

from .models import CustomUser, Notification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': (('first_name', 'last_name'), 'email', 'friends')}),
        (('Permissions'), {
            'fields': (('is_active', 'is_staff', 'is_superuser'), 'groups', 'user_permissions'),
        }),
        (('Important dates'), {'fields': (('date_joined', 'last_login'), )}),
    )
    inlines = [MembershipInline]


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'content_type', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'content_type')
    search_fields = ('user__username', 'message')
