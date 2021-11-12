from rest_framework.permissions import IsAuthenticated

from apps.utils.filters import URLRelatedFilter, UserRelatedFilter
from apps.utils.permissions import IsManyRelated
from apps.utils.views import ListCRUDViewSet, ListRetrieveViewSet

from apps.chats.models import Chat, Membership, Message
from apps.chats.permissions import (
    IsChatAdminOrMessageSender, 
    IsChatAdminOrReadOnly, 
    IsChatMember, 
    IsChatAdminIfChange
)
from .serializers import (
    ChatSerializer,
    MembershipSerializer,
    APIMessageSerializer, 
)

class ChatViewSet(ListCRUDViewSet):
    permission_classes = [IsAuthenticated, IsManyRelated, IsChatAdminOrReadOnly]
    filter_backends = [UserRelatedFilter]
    user_field = 'members'

    serializer_class = ChatSerializer
    queryset = Chat.objects.all()


class ChatMembersViewSet(ListCRUDViewSet):
    permission_classes = [IsAuthenticated, IsChatMember, IsChatAdminIfChange]
    filter_backends = [URLRelatedFilter]
    url_related_field = 'chat_id'
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


class ChatMessageViewSet(ListRetrieveViewSet):
    permission_classes = [IsAuthenticated, IsChatMember, IsChatAdminOrMessageSender]
    filter_backends = [URLRelatedFilter]
    url_related_field = 'chat_id'
    url_related_kwarg = 'chat_pk'

    serializer_class = APIMessageSerializer
    queryset = Message.objects.all()
