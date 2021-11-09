from django.contrib.auth import get_user_model

from rest_framework import serializers

from apps.accounts.models import Notification


UserModel = get_user_model()


class UserCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('pk', 'username', 'first_name', 'last_name')


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'friends')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            'pk', 'user', 'type', 'message', 
            'content_type', 'object_id', 
            'is_read', 'created_at'
        )
        