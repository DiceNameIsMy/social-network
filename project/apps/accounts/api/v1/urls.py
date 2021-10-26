from django.urls import path, include

from .views import (
    UserListView,
    UserRetrieveView,
    UserFriendsView
)

urlpatterns = [
    path('users/', UserListView.as_view()),
    path('users/<int:pk>/', UserRetrieveView.as_view()),
    path('users/<int:pk>/friends/', UserFriendsView.as_view()),

    path('auth/', include('dj_rest_auth.urls')),
    # path('auth/user/chats/', _.as_view()),
    path('auth/signup/', include('dj_rest_auth.registration.urls'))
]
