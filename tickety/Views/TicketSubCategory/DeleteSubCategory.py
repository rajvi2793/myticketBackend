from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed


@api_view(['DELETE'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def delete_ticket_subcategory_by_transid(request, transid):
    try:
        # Retrieve the ticket subcategory with the specified transid
        ticket_subcategory = QitTicketsubcategory.objects.get(transid=transid)
        
        # Delete the ticket subcategory
        ticket_subcategory.delete()
        
        # Return response confirming deletion
        return Response({'message': 'Ticket subcategory deleted successfully'}, status=status.HTTP_200_OK)

    except QitTicketsubcategory.DoesNotExist:
        # Handle case where the subcategory is not found
        return Response({'error': 'Ticket subcategory not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # Handle other errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
