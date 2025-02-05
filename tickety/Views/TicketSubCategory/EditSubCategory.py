from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed


@api_view(['PUT'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def edit_ticket_subcategory(request, transid):
    """Edit an existing ticket subcategory."""
    try:
        # Fetch the subcategory to be updated
        ticket_subcategory = QitTicketsubcategory.objects.get(transid=transid)
    except QitTicketsubcategory.DoesNotExist:
        return Response({'error': 'Ticket subcategory not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Deserialize and validate the data
    serializer = QitTicketsubcategorySerializer(ticket_subcategory, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Ticket Subcategory updated successfully!', 'data': serializer.data}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
