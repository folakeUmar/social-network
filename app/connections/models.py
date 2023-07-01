from django.db import models

from core.models import AuditableModel
from .enums import CONNECTION_STATUS


class Connection(AuditableModel):
    sender = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="connect_sender" )
    receiver = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="connect_receiver")
    status = models.CharField(max_length=255, choices=CONNECTION_STATUS)
    # connected = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sender', 'receiver')

    def __str__(self):
        return f'{self.sender.first_name} - {self.receiver.first_name}'
    
    # def save_connected(self, status):
    #     if self.status == 'ACCEPTED':
    #         self.connected = True
            