from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_ticket_subcategory_by_transid(request, transid):
    try:
        # Retrieve the ticket subcategory with the specified transid
        ticket_subcategory = QitTicketsubcategory.objects.select_related('ticketcategorytransid').get(transid=transid)

        # Prepare response data with ticketcategoryname
        response_data = {
            "transid": ticket_subcategory.transid,
            "ticketsubcatname": ticket_subcategory.ticketsubcatname,
            "ticketsubiddeleted": ticket_subcategory.ticketsubiddeleted,
            "entry_date": ticket_subcategory.entry_date,
            "update_date": ticket_subcategory.update_date,
            "companytransid": ticket_subcategory.companytransid_id,
            "ticketcategorytransid": ticket_subcategory.ticketcategorytransid_id,
            "ticketcategoryname": ticket_subcategory.ticketcategorytransid.ticketcategoryname if ticket_subcategory.ticketcategorytransid else None
        }

        # Return response with data
        return Response({'message': 'Ticket subcategory retrieved successfully', 'data': response_data}, status=status.HTTP_200_OK)

    except QitTicketsubcategory.DoesNotExist:
        # Handle case where the subcategory is not found
        return Response({'error': 'Ticket subcategory not found'}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        # Handle other errors
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_all_ticket_subcategories(request):
    try:
        # Retrieve all ticket subcategories with related ticket categories
        ticket_subcategories = QitTicketsubcategory.objects.select_related('ticketcategorytransid').all()
        
        # Prepare response data with ticketcategoryname
        response_data = []
        for subcategory in ticket_subcategories:
            response_data.append({
                "transid": subcategory.transid,
                "ticketsubcatname": subcategory.ticketsubcatname,
                "ticketsubiddeleted": subcategory.ticketsubiddeleted,
                "entry_date": subcategory.entry_date,
                "update_date": subcategory.update_date,
                "companytransid": subcategory.companytransid_id,
                "ticketcategorytransid": subcategory.ticketcategorytransid_id,
                "ticketcategoryname": subcategory.ticketcategorytransid.ticketcategoryname if subcategory.ticketcategorytransid else None
            })
        
        # Return response with data
        return Response({'message': 'All ticket subcategories retrieved successfully', 'data': response_data}, status=status.HTTP_200_OK)
    
    except Exception as e:
        # Handle errors if something goes wrong
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
