from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed

@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def save_ticket_subcategory(request):
    """Save a new ticket subcategory."""
    serializer = QitTicketsubcategorySerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Ticket Subcategory saved successfully!','data': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

