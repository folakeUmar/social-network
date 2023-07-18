from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import ConnectRequestSerializer, ConnectionStatusUpdateSerializer

from .models import Connection


class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectRequestSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']

    # def get_serializer(self, *args, **kwargs):
    def get_serializer_class(self):
        if self.action in ['send_request', 'view_connection_request']:
            return ConnectRequestSerializer
        elif self.action == 'connection_request_response':
            return ConnectionStatusUpdateSerializer
        # return super().get_serializer(*args, **kwargs)
        return super().get_serializer_class()
    
    @action(
        methods=['POST'],
        detail=False,
        url_path='sender-request',
    )
    def send_request(self, request):
        serializer = self.get_serializer(data=request.data) 
        # print(serializer.is_valid())
        if serializer.is_valid(raise_exception=True):
            serializer.save(sender=request.user, status='PENDING')
        return Response({'success':True, 'message':'connection request successfully sent'}, status=status.HTTP_200_OK)

    @action(
            methods = ['GET'],
            detail = False,
            url_path='display-requests'
    )
    def view_connection_request(self, request):
        connection_request = self.queryset.filter(receiver=request.user, status='PENDING')
        serializer = self.get_serializer(connection_request, many=True)
        return Response({'success':True, 'data':serializer.data}, status=status.HTTP_200_OK)

    @action(
        methods=['PATCH'],
        detail=True,
        url_path='connection-request-response'
    )
    def connection_request_response(self, request, pk=None):
        connection_request = self.get_object()
        serializer = self.get_serializer(data=request.data, instance=connection_request)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': f'connection request {request.user.status}'})
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST) 
     
# accept connection request
# logged in user = receiver
# view all request filtering by sender
# loop through all the requests one after the other
# display different statuses of connection for user to select
# save connection.status
# return 





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



'''
To accept connection requests:

create an update method

1. create an endpoint to display all the people with status (ACCEPTED) in request.user connection
2. filter out all pending statuses...Connection.objects.filter(status='PENDING', receiver=request.user)
3. [connection for connection in pending_connections] 
3. check validatated statuses and update accordingly
4. status = validated_data['status']
        if status:
             instance.status = status
                instance.save()
                return instance
'''

# class ConnectionStatusUpdateSerializer(serializers.Serializer):
#     status = serializers.ChoiceField(choices=CONNECTION_STATUS)

#     def update(self, instance, validated_data):
#         pending_connections = self.context['pending_connections']
#         if pending_connections:
#             pending_connection = [pending_connection for pending_connection in pending_connections]
#             if pending_connection:
#                 status = validated_data['status']
#                 instance.status = status
#                 instance.save()
#                 return instance