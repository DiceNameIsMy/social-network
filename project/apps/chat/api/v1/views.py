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

from apps.utils.filters import URLRelatedFilter
from apps.utils.permissions import IsManyRelated
from apps.chat.models import Chat, Membership, Message
from apps.chat.permissions import IsChatMember

from .serializers import (
    ChatSerializer,
    MembershipSerializer,
    MessageSerializer, 
)

UserModel = get_user_model()


class ChatListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = ChatSerializer
    queryset = Chat.objects.all()        


class ChatRetrieveDestroyView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsManyRelated]
    related_field = 'members'

    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


# Chat related
class ChatMembersListAddView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsChatMember]
    filter_backends = [URLRelatedFilter]
    url_related_field = 'chat'
    url_related_kwarg = 'chat_pk'

    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()


class ChatMemberRetriveExpelView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsChatMember]
    url_related_field = 'chat'
    url_related_kwarg = 'chat_pk'

    serializer_class = MembershipSerializer
    queryset = Membership.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.chat.type == Chat.Type.DIRECT:
            return Response(
                data={'detail': 'Not allowed'}, status=400
            )
        self.perform_destroy(instance)
        return Response(status=204)
        

class ChatMessageListCreateView(ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsChatMember]
    filter_backends = [URLRelatedFilter]
    url_related_field = 'chat_id'
    url_related_kwarg = 'chat_pk'

    serializer_class = MessageSerializer
    queryset = Message.objects.all()


class ChatMessageRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsChatMember]
    filter_backends = [URLRelatedFilter]
    url_related_field = 'chat_id'
    url_related_kwarg = 'chat_pk'

    serializer_class = MessageSerializer
    queryset = Message.objects.all()

