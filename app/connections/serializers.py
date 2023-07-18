from rest_framework import serializers, exceptions
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Connection
from .enums import CONNECTION_STATUS


class ConnectRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Connection
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'sender': {'read_only': True},
            'created_at': {'read_only': True},
            'status': {'read_only': True},
        }


class ConnectionStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=CONNECTION_STATUS, required=True)

    def update(self, instance, validated_data):
        status = validated_data['status']
        instance.status = status
        instance.save()
        return instance
