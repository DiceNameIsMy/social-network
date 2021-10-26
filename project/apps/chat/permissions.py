from rest_framework.permissions import BasePermission


class IsChatMember(BasePermission):
    message = 'user have to be chat member'

    def has_permission(self, request, view):
        chat_pk = view.kwargs[view.url_related_kwarg]
        return bool(
            chat_pk in request.user.chats.all().values_list('pk', flat=True)
        )


class IsChatMemberOrAdmin(BasePermission):
    message = 'user have to be chat member or admin'

    def has_permission(self, request, view):
        chat_pk = view.kwargs[view.url_related_kwarg]
        return bool(
            request.user.is_staff or
            chat_pk in request.user.chats.all().values_list('pk', flat=True)
        )