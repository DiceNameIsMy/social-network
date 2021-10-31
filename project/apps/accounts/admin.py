from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.chats.admin import MembershipInline

from .models import CustomUser


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
