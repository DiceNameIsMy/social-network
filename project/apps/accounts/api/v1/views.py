from django.contrib.auth import get_user_model

from rest_framework.generics import (
    GenericAPIView,
    ListAPIView, 
    RetrieveAPIView, 
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.chats.models import Chat
from apps.chats.api.v1.serializers import ChatSerializer
from apps.utils.filters import URLRelatedFilter, UserRelatedFilter
from apps.accounts.models import Notification
from apps.utils.permissions import IsRelated

from .serializers import NotificationSerializer, UserCardSerializer, UserDetailSerializer


UserModel = get_user_model()


class UserListView(ListAPIView):
    serializer_class = UserCardSerializer
    queryset = UserModel.objects.all()


class UserRetrieveView(RetrieveAPIView):
    serializer_class = UserDetailSerializer
    queryset = UserModel.objects.all()


class UserFriendsView(ListAPIView):
    filter_backends = [URLRelatedFilter]
    url_related_field = 'friends'
    url_related_kwarg = 'pk'

    serializer_class = UserCardSerializer
    queryset = UserModel.objects.all()


class UserChatsView(ListAPIView):
    filter_backends = [UserRelatedFilter]
    user_field = 'members'

    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


class NotificationMarkAsRead(GenericAPIView):
    permission_classes = [IsAuthenticated, IsRelated]
    related_field = 'user'

    serializer_class = NotificationSerializer
    queryset = Notification.objects.all().only('pk', 'is_read')

    def patch(self, request, *args, **kwargs):
        """ Mark notification as read """
        obj: Notification = self.get_object()
        obj.is_read = True
        obj.save()
        serializer = self.get_serializer(obj)
        return Response(serializer.data)


class UserNotificationListView(ListAPIView):
    filter_backends = [UserRelatedFilter]
    user_field = 'user'

    serializer_class = NotificationSerializer
    queryset = Notification.objects.all()


class UserUnreadNotificationListView(ListAPIView):
    filter_backends = [UserRelatedFilter]
    user_field = 'user'

    serializer_class = NotificationSerializer
    queryset = Notification.objects.filter(is_read=False)
    