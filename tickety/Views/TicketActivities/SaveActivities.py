from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from tickety.models import QitActivities,QitTickets,QitCompanycustomer,QitCompanyuser,QitTicketcategory,QitTicketsubcategory,QitTicketnotes,QitTickettimespent,QitCompany,QitNotifications
from tickety.serializers import QitActivitiesSerializer,ToggleTicketStatusSerializer
from tickety.serializers import QitActivitiesCreateSerializer
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.core.files.base import ContentFile
from django.db import transaction
from datetime import datetime
import base64
from django.utils import timezone
from django.utils.timezone import now


@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
@transaction.atomic
def create_ticket_activity(request):
    toggle_status_serializer = ToggleTicketStatusSerializer(data=request.data)

    if not toggle_status_serializer.is_valid():
        return Response(toggle_status_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    ticketcode = toggle_status_serializer.validated_data["ticketcode"]
    new_status = toggle_status_serializer.validated_data["isStatus"]
    creatorcode = toggle_status_serializer.validated_data.get("creatorcode")
    companytransid = request.data.get("companytransid")
    activitydatetime = request.data.get("activitydatetime", datetime.now())

    # Fetch the ticket instance
    try:
        ticket = QitTickets.objects.select_related(
            'ticketcategorytransid', 'ticketsubcattransid', 'companytransid', 'customertransid', 'usertransid'
        ).get(ticketcode=ticketcode)
    except QitTickets.DoesNotExist:
        return Response({"message": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    # Update ticket details if provided
    ticket.ticketpriority = request.data.get('ticketpriority', ticket.ticketpriority)

    ticketcategory_id = request.data.get('ticketcategorytransid')
    if ticketcategory_id:
        try:
            ticket.ticketcategorytransid = QitTicketcategory.objects.get(transid=ticketcategory_id)
        except QitTicketcategory.DoesNotExist:
            return Response({"message": "Invalid ticket category ID."}, status=status.HTTP_400_BAD_REQUEST)

    ticketsubcat_id = request.data.get('ticketsubcattransid')
    if ticketsubcat_id:
        try:
            ticket.ticketsubcattransid = QitTicketsubcategory.objects.get(transid=ticketsubcat_id)
        except QitTicketsubcategory.DoesNotExist:
            return Response({"message": "Invalid ticket subcategory ID."}, status=status.HTTP_400_BAD_REQUEST)

    # Update ticket status and save
    ticket.ticketstatus = new_status
    ticket.save()

    # Determine the activitydoneby and validate companytransid or creatorcode
    activitydoneby = None
    if companytransid:
        try:
            company = QitCompany.objects.get(transid=companytransid)
            activitydoneby = company.companyname
        except QitCompany.DoesNotExist:
            return Response({"message": "Invalid companytransid."}, status=status.HTTP_404_NOT_FOUND)
    elif creatorcode:
        try:
            user = QitCompanyuser.objects.get(cmpusercode=creatorcode)
            activitydoneby = user.cmpuserusername
        except QitCompanyuser.DoesNotExist:
            return Response({"message": "Invalid creatorcode."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({"message": "Either companytransid or creatorcode must be provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Set activity type and message based on status update or custom message
    activitytype = "Status Update"
    activity_message = f"Ticket status updated to '{new_status}'."

    # Create a ticket activity for the current ticket
    activity = QitActivities.objects.create(
        activitydatetime=activitydatetime,
        tickettransid=ticket,
        activitydoneby=activitydoneby,
        creatorcode=creatorcode if creatorcode else companytransid,
        activitytype=activitytype,
        activity_message=activity_message,
    )

    # Update the working_user field of the ticket with the activitydoneby value
    ticket.working_user = activitydoneby
    ticket.save()

    QitNotifications.objects.create(
        title=f"Ticket '{ticketcode}' status updated to '{new_status}'.",
        description=f"Ticket '{ticketcode}' status updated to '{new_status}'.",
        notificationtype="Status Update",
        notificationstatus="unread",
        usertransid=ticket.usertransid if ticket.usertransid else None,
        companytransid=ticket.companytransid if ticket.companytransid else None,
        activitytransid=activity,
        createdby=activitydoneby,
        entrydate=now(),
    )

    # Grouping activities based on ticketcode
    activities = QitActivities.objects.filter(tickettransid=ticket).order_by('activitydatetime')

    # Prepare response data
    response_data = {
        "message": f"Ticket status updated to '{new_status}' and activity created successfully.",
        "ticket": {
            "ticketcode": ticket.ticketcode,
            "ticketstatus": ticket.ticketstatus,
            "ticketpriority": ticket.ticketpriority,
            "ticketsubject": ticket.ticketsubject,
            "ticketcategoryname": ticket.ticketcategorytransid.ticketcategoryname if ticket.ticketcategorytransid else None,
            "ticketsubcatname": ticket.ticketsubcattransid.ticketsubcatname if ticket.ticketsubcattransid else None,
        },
        "activities": [
            {
                "transid": act.transid,
                "activitydatetime": act.activitydatetime,
                "tickettransid": act.tickettransid.transid,
                "activitydoneby": act.activitydoneby,
                "creatorcode": act.creatorcode,
                "entry_date": act.entry_date,
                "update_date": act.update_date,
                "activitytype": act.activitytype,
                "activity_message": act.activity_message,
            }
            for act in activities
        ],
        "customer_name": ticket.customertransid.custname if ticket.customertransid else None,
        "user_username": ticket.usertransid.cmpuserusername if ticket.usertransid else None,
        "company_name": ticket.companytransid.companyname if ticket.companytransid else None,
        "working_user": ticket.working_user,  # Include working_user in the response
    }

    return Response(response_data, status=status.HTTP_200_OK)

