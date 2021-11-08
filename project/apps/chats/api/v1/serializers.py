from django.contrib.auth import get_user_model
from django.db import transaction

from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from apps.chats.models import Chat, Membership, Message


UserModel = get_user_model()


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['pk', 'type', 'user', 'chat']

        validators = [
            UniqueTogetherValidator(
                queryset=Membership.objects.all(),
                fields=['user', 'chat'],
                message='user is already in chat'
            )
        ]

    def to_internal_value(self, data):
        data = data.copy()
        data['chat'] = self.context['view'].kwargs[self.context['view'].url_related_kwarg]

        return super().to_internal_value(data)

    # TODO validation that only 2 users allowed if chat type is direct

class _MembershipCreateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['pk', 'type', 'user', 'chat']

        validators = [
            UniqueTogetherValidator(
                queryset=Membership.objects.all(),
                fields=['user', 'chat'],
                message='user is already in chat'
            )
        ]


class ChatSerializer(serializers.ModelSerializer):
    # TODO improve ugly long serialization
    
    memberships = _MembershipCreateSerialzier(
        many=True, 
    )
    class Meta:
        model = Chat
        fields = ['pk', 'title', 'type', 'memberships', 'members_amount']
        depth = 1

    def to_internal_value(self, data):
        if data.get('memberships'):
            user_pk = self.context['request'].user.pk
            data['memberships'].append(
                {'user': user_pk, 'type': Membership.Type.ADMIN}
            )
            for member in data['memberships']:
                member.setdefault('type', Membership.Type.REGULAR)
                member['chat'] = None

        return super().to_internal_value(data)

    def validate(self, attrs):
        if attrs.get('type') == Chat.Type.DIRECT:
            if len(attrs.get('memberships')) != 2:
                raise serializers.ValidationError(
                    'direct chat should have 2 members'
                )

            user_pks = [
                membership['user'].pk for membership in attrs['memberships']
            ]
            same_chat_exists = Chat.objects.filter(
                type=Chat.Type.DIRECT,
                members=user_pks[0]
            ).filter(
                members=user_pks[1]
            ).exists()

            if same_chat_exists:
                raise serializers.ValidationError(
                    'direct chats should be unique'
                )
                
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        Model = self.Meta.model
        membership_data = validated_data.pop('memberships')
        instance = Model.objects.create(**validated_data)

        for member_data in membership_data:
            member_data['chat'] = instance
        
        members = [
            Membership(**member_data) for member_data in membership_data
        ]
        Membership.objects.bulk_create(members)

        return instance


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['pk', 'chat', 'sender', 'username', 'datetime', 'text']
    
    def to_internal_value(self, data):
        data: dict = data.copy()
        data['chat'] = self.context['view'].kwargs[self.context['view'].url_related_kwarg]
        data['sender'] = self.context['request'].user.id
        return super().to_internal_value(data)


class RoutingMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['pk', 'chat', 'sender', 'username', 'datetime', 'text']


