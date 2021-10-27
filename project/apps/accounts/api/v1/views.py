from django.contrib.auth import get_user_model

from rest_framework.generics import (
    ListAPIView, 
    RetrieveAPIView, 
    RetrieveUpdateAPIView
)

from apps.chat.models import Chat
from apps.chat.api.v1.serializers import ChatSerializer
from apps.utils.filters import URLRelatedFilter, UserRelatedFilter

from .serializers import UserCardSerializer, UserDetailSerializer


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
