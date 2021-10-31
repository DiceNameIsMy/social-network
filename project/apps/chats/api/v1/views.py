from django.contrib.auth import get_user_model

from rest_framework.generics import (
    get_object_or_404,
    ListAPIView,
    ListCreateAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
    DestroyAPIView
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from apps.utils.filters import URLRelatedFilter, UserRelatedFilter
from apps.utils.permissions import IsManyRelated
from apps.chats.models import Chat, Membership, Message
from apps.chats.permissions import IsChatAdminOrMessageSender, IsChatAdminOrReadOnly, IsChatMember, IsChatAdminIfChange

from .serializers import (
    ChatSerializer,
    MembershipSerializer,
    MessageSerializer, 
)

UserModel = get_user_model()


class ChatListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [UserRelatedFilter]
    user_field = 'members'

    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


class ChatRetrieveDestroyView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManyRelated, IsChatAdminOrReadOnly]
    related_field = 'members'

    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


# Chat related
class ChatMembersListAddView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsChatMember, IsChatAdminIfChange]
    filter_backends = [URLRelatedFilter]
    url_related_field = 'chat_id'
    url_related_kwarg = 'chat_pk'

    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()


class ChatMemberRetriveExpelView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsChatMember, IsChatAdminIfChange]
    url_related_field = 'chat'
    url_related_kwarg = 'chat_pk'

    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()

    def check_object_permissions(self, request, obj):
        if request.method == 'DELETE' and obj.chat.type == Chat.Type.DIRECT:
            self.permission_denied(
                request,
                message='direct chat memeber expelling is not allowed',
                code=400
            )
        super().check_object_permissions(request, obj)


class ChatMessageListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsChatMember]
    filter_backends = [URLRelatedFilter]
    url_related_field = 'chat_id'
    url_related_kwarg = 'chat_pk'

    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class ChatMessageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsChatAdminOrMessageSender]
    filter_backends = [URLRelatedFilter]
    url_related_field = 'chat_id'
    url_related_kwarg = 'chat_pk'

    serializer_class = MessageSerializer
    queryset = Message.objects.all()

