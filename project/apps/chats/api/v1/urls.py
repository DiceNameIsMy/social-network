from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    ChatViewSet,
    ChatMessageViewSet,
    ChatMembersViewSet,
)
router = DefaultRouter()
router.register('', ChatViewSet, basename='chats')
router.register(r'(?P<chat_pk>\w+)/messages', ChatMessageViewSet, basename='messages')
router.register(r'(?P<chat_pk>\w+)/members', ChatMembersViewSet, basename='members')


urlpatterns = [
    path('', include(router.urls)),
]