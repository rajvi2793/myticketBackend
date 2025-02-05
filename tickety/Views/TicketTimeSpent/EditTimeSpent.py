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

@api_view(['PUT'])
@authentication_classes([auth_views.CustomAuthentication])
def update_ticket_time_spent(request, pk):
    try:
        # Fetch the ticket time spent entry
        try:
            ticket_time_spent = QitTickettimespent.objects.get(transid=pk)
        except QitTickettimespent.DoesNotExist:
            return Response({"detail": "Time spent record not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Extract data from the request
        data = request.data
        ticketcode = data.get('ticketcode')
        usertransid = data.get('usertransid')  # User ID
        companytransid = data.get('companytransid')  # Company ID
        starttime_str = data.get('starttime')
        endtime_str = data.get('endtime')
        start_date = data.get('start_date')  # Get start_date from request
        description = data.get('description')

        # Parse starttime and endtime into the required format
        try:
            starttime = datetime.strptime(starttime_str, "%I:%M:%S %p").time() if starttime_str else ticket_time_spent.starttime
            endtime = datetime.strptime(endtime_str, "%I:%M:%S %p").time() if endtime_str else ticket_time_spent.endtime
        except ValueError:
            return Response({"detail": "Invalid time format. Use 'HH:MM:SS AM/PM' format."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate start_date format (only date part: YYYY-MM-DD)
        # if start_date:
        #     try:
        #         start_date = datetime.strptime(start_date, '%Y-%m-%d').date()  # Parse only the date (no time part)
        #     except ValueError:
        #         return Response({"detail": "Invalid start_date format. Use 'YYYY-MM-DD'."}, status=status.HTTP_400_BAD_REQUEST)

        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%d-%m-%Y').date()  # Parse to date (dd-mm-yyyy format)
            except ValueError:
                return Response({"detail": "Invalid start_date format. Use 'dd-mm-yyyy'."}, status=status.HTTP_400_BAD_REQUEST)


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

        # Fetch user or company name and set updated_by
        if usertransid:
            try:
                user = QitCompanyuser.objects.get(transid=usertransid)
                updated_by = user.cmpuserusername  # User's name
            except QitCompanyuser.DoesNotExist:
                return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                company = QitCompany.objects.get(transid=companytransid)
                updated_by = company.companyname  # Company's name
            except QitCompany.DoesNotExist:
                return Response({"detail": "Company not found."}, status=status.HTTP_404_NOT_FOUND)

        # Update the ticket time spent entry
        ticket_time_spent.starttime = starttime
        ticket_time_spent.endtime = endtime
        ticket_time_spent.start_date = start_date if start_date else ticket_time_spent.start_date  # Update start_date
        ticket_time_spent.description = description if description else ticket_time_spent.description
        ticket_time_spent.updated_by = updated_by  # Set updated_by
        ticket_time_spent.save()

        # Log the update activity in QitActivities
        activity_entry = QitActivities.objects.create(
            tickettransid=ticket,
            activitytype="Time Spent Updated",
            activitydatetime=now(),
            activitydoneby=updated_by,
            creatorcode=usertransid if usertransid else companytransid,
            update_date=now(),
            activity_message=f"Time spent of Updated for ticket: {ticketcode}: {description}."  # Use updated description as the activity message
        )

        # Add notification entry to QitNotifications
        notification_entry = QitNotifications.objects.create(
            title=f"Time Spent Updated for ticket- {ticketcode} updated. New time: {starttime} - {endtime}.",
            description=f"Time spent for ticket: {ticketcode} updated. New time: {starttime} - {endtime}.",
            notificationtype="Time Spent Update",
            notificationstatus="unread",
            usertransid=QitCompanyuser.objects.get(transid=usertransid) if usertransid else None,
            companytransid=QitCompany.objects.get(transid=companytransid) if companytransid else None,
            activitytransid=activity_entry,
            createdby=updated_by,
            entrydate=now(),
        )

        # Prepare the response
        response_data = {
            "message": "Time spent updated and activity recorded successfully.",
            "timespent": {
                "transid": ticket_time_spent.transid,
                "starttime": ticket_time_spent.starttime,
                "endtime": ticket_time_spent.endtime,
                "start_date": ticket_time_spent.start_date,  # Include start_date in the response
                "description": ticket_time_spent.description,
                "updated_by": ticket_time_spent.updated_by,  # Include updated_by
                "update_date": ticket_time_spent.update_date,  # Include update_date
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

        return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

