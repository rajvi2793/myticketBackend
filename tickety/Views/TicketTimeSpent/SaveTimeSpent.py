from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.serializers import QitTicketTimeSpentSerializer
from tickety.models import QitTickettimespent,QitActivities,QitTickets,QitCompanyuser,QitCompany,QitNotifications
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.utils import timezone
from django.utils.timezone import now
from datetime import datetime

def convert_time_to_24_hour_format(time_str):
    try:
        return datetime.strptime(time_str, "%I:%M:%S %p").time()
    except ValueError:
        raise ValueError(f"Invalid time format: {time_str}. Use HH:MM:SS AM/PM format.")


@api_view(['POST'])  
@authentication_classes([auth_views.CustomAuthentication])
def save_QitTicketspent(request):
    """
    Save time spent for a ticket and log the activity in the QitActivities table.
    The current date is automatically set for the time spent when the save action is performed.
    """
    try:
        # Extract data from the request
        data = request.data
        ticketcode = data.get('ticketcode')
        usertransid = data.get('usertransid')  # User ID
        companytransid = data.get('companytransid')  # Company ID
        starttime = data.get('starttime')
        endtime = data.get('endtime')
        start_date = data.get('start_date')  # New field
        currentdate = now().date()  # Automatically set to today's date
        description = data.get('description')

        # Validate start_date format to dd-mm-yyyy
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%d-%m-%Y').date()  # Parse to date (dd-mm-yyyy format)
            except ValueError:
                return Response({"detail": "Invalid start_date format. Use 'dd-mm-yyyy'."}, status=status.HTTP_400_BAD_REQUEST)

        # Convert time format
        try:
            starttime = convert_time_to_24_hour_format(starttime)
            endtime = convert_time_to_24_hour_format(endtime)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Validate ticket
        try:
            ticket = QitTickets.objects.get(ticketcode=ticketcode)
        except QitTickets.DoesNotExist:
            return Response({"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure either usertransid or companytransid is provided, but not both
        if usertransid and companytransid:
            return Response({"detail": "Provide only one of usertransid or companytransid."}, status=status.HTTP_400_BAD_REQUEST)
        if not usertransid and not companytransid:
            return Response({"detail": "Either usertransid or companytransid must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch user or company name and set creatorcode and activitydoneby
        if usertransid:
            try:
                user = QitCompanyuser.objects.get(transid=usertransid)
                activitydoneby = user.cmpuserusername  # User's name
                creatorcode = usertransid  # Set creatorcode to usertransid
            except QitCompanyuser.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                company = QitCompany.objects.get(transid=companytransid)
                activitydoneby = company.companyname  # Company's name
                creatorcode = companytransid  # Set creatorcode to companytransid
            except QitCompany.DoesNotExist:
                return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        # Save time spent entry
        time_entry = QitTickettimespent.objects.create(
            tickettransid=ticket,
            starttime=starttime,
            endtime=endtime,
            currentdate=currentdate,
            start_date=start_date,  # Store start_date in dd-mm-yyyy format
            usertransid=QitCompanyuser.objects.get(transid=usertransid) if usertransid else None,
            companytransid=QitCompany.objects.get(transid=companytransid) if companytransid else None,
            description=description
        )

        # Add a corresponding entry in QitActivities
        activity_entry = QitActivities.objects.create(
            tickettransid=ticket,
            activitytype="Time Spent",
            activitydatetime=now(),
            activitydoneby=activitydoneby,
            creatorcode=creatorcode,  # Use dynamically set creatorcode
            entry_date=currentdate,
            update_date=now(),
            activity_message=f"Time spent Added for ticket-{ticketcode}: {description}.",  # Use description as the activity message
        )

        # Add notification entry to QitNotifications
        notification_entry = QitNotifications.objects.create(
            title=f"Time spent of {starttime} - {endtime} recorded for ticket: {ticketcode}.",
            description=f"Time spent of {starttime} - {endtime} recorded for ticket: {ticketcode}.",
            notificationtype="Time Spent",
            notificationstatus="unread",
            usertransid=QitCompanyuser.objects.get(transid=usertransid) if usertransid else None,
            companytransid=QitCompany.objects.get(transid=companytransid) if companytransid else None,
            activitytransid=activity_entry,
            createdby=activitydoneby,
            entrydate=now(),
        )

        # Prepare response
        response_data = {
            "message": "Time spent saved and activity recorded successfully.",
            "timespent": {
                "transid": time_entry.transid,
                "starttime": time_entry.starttime,
                "endtime": time_entry.endtime,
                "currentdate": time_entry.currentdate,
                "start_date": time_entry.start_date,  # Include start_date in response (dd-mm-yyyy format)
                "description": time_entry.description,
            },
            "activity": {
                "transid": activity_entry.transid,
                "activitytype": activity_entry.activitytype,
                "activitydatetime": activity_entry.activitydatetime,
                "activitydoneby": activity_entry.activitydoneby,
                "creatorcode": activity_entry.creatorcode,
                "activity_message": activity_entry.activity_message,
            },
            "notification": {
                "transid": notification_entry.transid,
                "title": notification_entry.title,
                "description": notification_entry.description,
                "notificationtype": notification_entry.notificationtype,
                "createdby": notification_entry.createdby,
                "notificationstatus": notification_entry.notificationstatus,
            }
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


