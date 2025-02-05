from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser,QitActivities,QitNotifications,QitConfiguration
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer,ToggleTicketStatusSerializer,QitActivitiesSerializer,QitNotificationsSerializer
from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_tickets_by_customer(request):
    """Retrieve all tickets for a specific company and customer."""
    
    # Retrieve companytransid and customertransid from query parameters
    company_transid = request.query_params.get('companytransid')
    customer_transid = request.query_params.get('customertransid')

    # Ensure that both coxmpanytransid and customertransid are provided
    if not company_transid or not customer_transid:
        return Response({'error': 'You must provide both companytransid and customertransid.'}, status=status.HTTP_400_BAD_REQUEST)

    # Filter tickets by the provided companytransid and customertransid
    tickets = QitTickets.objects.filter(companytransid=company_transid, customertransid=customer_transid)

    # Check if tickets exist for the specified company and customer
    if not tickets.exists():
        return Response({'error': 'No tickets found for the specified company and customer.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize the filtered tickets
    serializer = QitTicketsSerializer(tickets, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

