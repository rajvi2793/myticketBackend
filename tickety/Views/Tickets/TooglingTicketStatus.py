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


@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def toggle_ticket_status(request):
    serializer = ToggleTicketStatusSerializer(data=request.data)
    if serializer.is_valid():
        ticketcode = serializer.validated_data["ticketcode"]
        new_status = serializer.validated_data["isStatus"]
        
        try:
            # Retrieve the ticket
            ticket = QitTickets.objects.get(ticketcode=ticketcode)
        except QitTickets.DoesNotExist:
            return Response(
                {"message": "Ticket not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        old_status = ticket.ticketstatus  # Store the old status before changing it

        # Normalize both ticket status and new status to lowercase for case-insensitive comparison
        if old_status.lower() == new_status.lower():
            return Response(
                {"message": f"Ticket status is already '{new_status}'."},
                status=status.HTTP_200_OK
            )

        # Update the status
        ticket.ticketstatus = new_status
        ticket.save()

        # Create a notification entry
        notification_data = {
            'title': f"Ticket {ticketcode} Status Changed",
            'description': f"Ticket {ticketcode} status changed from {old_status} to {new_status}.",
            'notificationtype': 'Ticket Status Update',
            'notificationstatus': 'Unread',  # Set as unread by default
            'tickettransid': ticket,  # Associate with the ticket
            'createdby': request.user.username if hasattr(request.user, 'username') else "Unknown",
            'entrydate': ticket.update_date,  # Use the ticket's updated date or current time
        }

        # Save the notification
        try:
            notification = QitNotifications.objects.create(**notification_data)
            notification.save()
        except Exception as e:
            return Response(
                {"message": f"Failed to create notification: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            {"message": f"Ticket status updated to '{new_status}' and notification created."},
            status=status.HTTP_200_OK
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



