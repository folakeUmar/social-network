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
     