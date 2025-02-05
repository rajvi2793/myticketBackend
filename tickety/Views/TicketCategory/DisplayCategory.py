from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.db import IntegrityError  # Import IntegrityError for handling foreign key constraint errors

@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_all_ticket_categories(request):
    try:
        # Retrieve all ticket category records
        ticket_categories = QitTicketcategory.objects.all()
        
        # Serialize the data
        serializer = QitTicketcategorySerializer(ticket_categories, many=True)
        
        # Return response with serialized data
        return Response({'message': 'All ticket categories retrieved successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Handle errors if something goes wrong
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

