from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import ConnectRequestSerializer

from .models import Connection


class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connection.objects.all()
    serializer_class = ConnectRequestSerializer
    http_method_names = ['post', 'get', 'delete']

    # def get_serializer(self, *args, **kwargs):
    def get_serializer_class(self):
        if self.action in ['send_request', 'display_requests']:
            return ConnectRequestSerializer
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
            url_path='display_requests'
    )
    def view_connection_request(self, request):
        connection_request = self.queryset.filter(receiver=request.user, status='PENDING')
        serializer = self.get_serializer(connection_request, many=True)
        return Response({'success':True, 'data':serializer.data}, status=status.HTTP_200_OK)
