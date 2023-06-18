from rest_framework import serializers, exceptions

from .models import Connect


class ConnectRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Connect
        fields = '__all__'
        extra_kwargs = {
            'id': {'read_only': True},
            'sender': {'read_only': True},
            'created_at': {'read_only': True},
            'status': {'read_only': True},
        }
