from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .serializers import ConnectRequestSerializer

from .models import Connect


class ConnectionViewSet(viewsets.ModelViewSet):
    queryset = Connect.objects.all()
    serializer_class = ConnectRequestSerializer
    http_method_names = ['post', 'get']

    def get_serializer(self, *args, **kwargs):
        if self.action == 'send_request':
            return ConnectRequestSerializer
        return super().get_serializer(*args, **kwargs)
    
    @action(
        methods=['POST'],
        detail=False,
        url_path='sender-request',
    )
    def sender_request(self, request):
        serializer = self.get_serializer(data=request.data, context={'sender':'request.user'}) 
        if serializer.is_valid():
            return Response({'success':True, 'message':'connection request successfully sent'}, status=status.HTTP_200_OK)
        
    