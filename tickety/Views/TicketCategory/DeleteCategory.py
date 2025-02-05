from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.db import IntegrityError  # Import IntegrityError for handling foreign key constraint errors


@api_view(['DELETE'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def delete_ticket_category(request, category_id):
    """Delete a ticket category along with related subcategories."""
    try:
        # Fetch the category to get its name
        category = QitTicketcategory.objects.get(transid=category_id)
        category_name = category.ticketcategoryname  # Assuming the category model has a 'name' field

        # Check if any tickets are using this category (through the subcategory)
        tickets_using_category = QitTickets.objects.filter(ticketsubcattransid__ticketcategorytransid=category_id)

        if tickets_using_category.exists():
            # Return a message if the category is being used in tickets
            return Response({
                'error': f'The ticket category "{category_name}" cannot be deleted because it is being used in one or more tickets.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Proceed with deleting the category and its related subcategories
        subcategories = QitTicketsubcategory.objects.filter(ticketcategorytransid=category)

        # Delete related subcategories
        subcategories.delete()

        # Delete the category
        category.delete()

        return Response({
            'message': f'Ticket category "{category_name}" and its related subcategories have been deleted successfully.'
        }, status=status.HTTP_200_OK)
    
    except QitTicketcategory.DoesNotExist:
        return Response({'error': f'Ticket category with ID {category_id} does not exist.'}, status=status.HTTP_404_NOT_FOUND)

    except IntegrityError:
        # Handle the foreign key constraint error
        return Response({
            'error': f'The ticket category "{category_name}" cannot be deleted because it is being used in somewhere else'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   