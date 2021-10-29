from django.urls import path, include

from .views import (
    UserChatsView,
    UserListView,
    UserRetrieveView,
    UserFriendsView
)

urlpatterns = [
    path('users/', UserListView.as_view()),
    path('users/<int:pk>/', UserRetrieveView.as_view()),
    path('users/<int:pk>/friends/', UserFriendsView.as_view()),

    path('', include('dj_rest_auth.urls')),
    path('user/chats/', UserChatsView.as_view()),
    path('signup/', include('dj_rest_auth.registration.urls'))
]
