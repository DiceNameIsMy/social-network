from django.urls import path, include

from rest_framework.routers import DefaultRouter

from .views import (
    ChatViewSet,
    ChatMessageViewSet,
    ChatMembersViewSet,
)
router = DefaultRouter()
router.register('', ChatViewSet, basename='chat')
router.register(r'(?P<chat_pk>\w+)/messages', ChatMessageViewSet, basename='message')
router.register(r'(?P<chat_pk>\w+)/members', ChatMembersViewSet, basename='member')


urlpatterns = [
    path('', include(router.urls)),
]