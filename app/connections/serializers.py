from rest_framework import serializers, exceptions

from .models import Connection


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


# from rest_framework import serializers, viewsets, status
# from rest_framework.response import Response
# from .models import Connection
# from django.contrib.auth.models import User

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username']

# class ConnectionSerializer(serializers.ModelSerializer):
#     sender = UserSerializer(read_only=True)
#     receiver = UserSerializer(read_only=True)

#     class Meta:
#         model = Connection
#         fields = ['id', 'sender', 'receiver', 'status', 'created_at']

# class ConnectionViewset(viewsets.ViewSet):
#     queryset = Connection.objects.all()
#     serializer_class = ConnectionSerializer

#     def list(self, request):
#         # Get connections where the current user is the receiver and status is 'pending'
#         connections = self.queryset.filter(receiver=request.user, status='pending')
#         serializer = self.serializer_class(connections, many=True)
#         return Response(serializer.data)

#     def update(self, request, pk=None):
#         connection = self.queryset.get(pk=pk)

#         # Check if the connection receiver is the current user
#         if connection.receiver == request.user:
#             # Accept the connection request
#             connection.status = 'accepted'
#             connection.save()
#             serializer = self.serializer_class(connection)
#             return Response(serializer.data)
#         else:
#             return Response(status=status.HTTP_403_FORBIDDEN)