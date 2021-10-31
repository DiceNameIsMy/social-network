from django.contrib import admin

from .models import Chat, Message, Membership


class MessageInline(admin.TabularInline):
    model = Message
    fields = ['text', ('sender', 'datetime')]
    readonly_fields = ['datetime']

    extra = 0


class MembershipInline(admin.TabularInline):
    model = Membership
    extra = 0


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ['title', 'type', 'members_amount']

    inlines = [MembershipInline, MessageInline]
