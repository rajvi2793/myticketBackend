from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.serializers import QitTicketTimeSpentSerializer
from tickety.models import QitTickettimespent,QitActivities,QitTickets,QitCompanyuser,QitCompany,QitNotifications
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.utils import timezone
from django.utils.timezone import now
from datetime import datetime


@api_view(['DELETE'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def delete_ticket_time_spent(request, pk):
    try:
        ticket_time_spent = QitTickettimespent.objects.get(transid=pk)
    except QitTickettimespent.DoesNotExist:
        return Response({'message': 'Record not found'}, status=status.HTTP_404_NOT_FOUND)

    ticket_time_spent.delete()
    return Response({'message': 'Record deleted successfully'}, status=status.HTTP_200_OK)

