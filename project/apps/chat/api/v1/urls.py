from django.urls import path, include

from .views import (
    ChatListCreateView,
    ChatRetrieveDestroyView,
    ChatMembersListAddView,
    ChatMemberRetriveExpelView,
    ChatMessageListCreateView,
    ChatMessageRetrieveUpdateDestroyView,
)

urlpatterns = [
    # Chat
    path('', ChatListCreateView.as_view(), name='all_user_common_chats'),
    path('<int:pk>/', ChatRetrieveDestroyView.as_view(), name='chat_detail'),
    
    # Chat related
    path('<int:chat_pk>/', include([
        path('members/', ChatMembersListAddView.as_view(), name='chat_members'),
        path('members/<int:pk>/', ChatMemberRetriveExpelView.as_view(), name='chat_member_detail'),

        path('messages/', ChatMessageListCreateView.as_view(), name='chat_messages'),
        path('messages/<int:pk>/', ChatMessageRetrieveUpdateDestroyView.as_view(), name='chat_message_detail'),
    ])),
]