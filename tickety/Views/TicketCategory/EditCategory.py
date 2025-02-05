from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.db import IntegrityError  # Import IntegrityError for handling foreign key constraint errors

@api_view(['PUT'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def edit_ticket_category(request, transid):
    """Edit an existing ticket category."""
    try:
        # Retrieve the ticket category by transid
        ticket_category = QitTicketcategory.objects.get(transid=transid)
    except QitTicketcategory.DoesNotExist:
        return Response({'error': 'Ticket category not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Serialize and validate incoming data
    serializer = QitTicketcategorySerializer(ticket_category, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Ticket category updated successfully!', 'data': serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    