from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.generics import get_object_or_404

from .models import Chat, Membership, Message


class IsChatAdminIfChange(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        
        membership = Membership.objects.all().get(
            user=request.user, chat_id=view.kwargs[view.url_related_kwarg]
        )
        return bool(
            membership.type == Membership.Type.ADMIN
        )


class IsChatMember(BasePermission):
    message = 'user have to be chat member'

    def has_permission(self, request, view):
        chat_pk = int(view.kwargs[view.url_related_kwarg])
        return bool(
            chat_pk in request.user.chats.all().values_list('pk', flat=True)
        )


class IsChatAdminOrReadOnly(BasePermission):
    message = 'you should be chat admin'

    def has_object_permission(self, request, view, obj):
        membership = obj.memberships.all().get(user=request.user)
        return bool(
            request.method in SAFE_METHODS or
            membership.type == Membership.Type.ADMIN
        )


class IsMessageSender(BasePermission):
    message = 'you should be message sender'

    def has_object_permission(self, request, view, obj):
        return bool(
            obj.sender_id == request.user.pk
        )

class IsChatAdminOrMessageSender(BasePermission):
    message = 'you have to be a message sender to make changes'

    def has_object_permission(self, request, view, obj):
        membership = Membership.objects.all().get(
            user=request.user, chat_id=view.kwargs[view.url_related_kwarg]
        )
        return bool(
            obj.sender_id == request.user.pk or
            membership.type == Membership.Type.ADMIN
        )
