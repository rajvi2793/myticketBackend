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


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_ticket_timespent(request, transid):
    """Retrieve ticket time spent record by transid."""
    try:
        # Fetch the ticket time spent record by transid
        ticket_time_spent = QitTickettimespent.objects.get(transid=transid)
        
        # Serialize the ticket time spent data
        serializer = QitTicketTimeSpentSerializer(ticket_time_spent)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except QitTickettimespent.DoesNotExist:
        return Response({"error": "Ticket time spent record not found."}, status=status.HTTP_404_NOT_FOUND)
    
