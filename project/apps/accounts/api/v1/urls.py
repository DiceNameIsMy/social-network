from django.urls import path, include

from .views import (
    NotificationMarkAsRead,
    UserChatsView,
    UserListView,
    UserNotificationListView,
    UserRetrieveView,
    UserFriendsView,
    UserUnreadNotificationListView
)

urlpatterns = [
    path('users/', UserListView.as_view()),
    path('users/<int:pk>/', UserRetrieveView.as_view()),
    path('users/<int:pk>/friends/', UserFriendsView.as_view()),

    path('notifications/<int:pk>/read/', NotificationMarkAsRead.as_view()),

    path('', include('dj_rest_auth.urls')),
    path('user/chats/', UserChatsView.as_view()),
    path('user/notifications/', UserNotificationListView.as_view()),
    path('user/notifications/unread/', UserUnreadNotificationListView.as_view()),
    path('signup/', include('dj_rest_auth.registration.urls'))
]
