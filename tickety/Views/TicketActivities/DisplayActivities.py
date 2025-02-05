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


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])
def ticket_activities_list_by_ticketcode(request, ticketcode):
    # Fetch the ticket based on ticketcode
    try:
        ticket = QitTickets.objects.get(ticketcode=ticketcode)
    except QitTickets.DoesNotExist:
        return Response({"detail": "Ticket not found."}, status=status.HTTP_404_NOT_FOUND)

    # Fetch all ticket activities related to the given ticketcode
    activities = QitActivities.objects.select_related(
        'tickettransid__ticketcategorytransid',
        'tickettransid__ticketsubcattransid',
        'tickettransid__companytransid',
        'tickettransid__customertransid',
        'tickettransid__usertransid'
    ).filter(tickettransid=ticket).all()

    # Fetch all timespent entries related to the given ticketcode
    timespent = QitTickettimespent.objects.filter(tickettransid=ticket).all()

    # Group data by ticketcode
    grouped_data = {
        "message": f"Activities and timespent retrieved for ticket '{ticketcode}'.",
        "ticket": {
            "ticketcode": ticket.ticketcode,
            "ticketstatus": ticket.ticketstatus,
            "ticketpriority": ticket.ticketpriority,
            "ticketsubject": ticket.ticketsubject,
            "ticketcategoryname": ticket.ticketcategorytransid.ticketcategoryname if ticket.ticketcategorytransid else None,
            "ticketsubcatname": ticket.ticketsubcattransid.ticketsubcatname if ticket.ticketsubcattransid else None,
            "ticketdescription": ticket.ticketdescription,
            "ticketattachedfile": ticket.ticketattachedfile,
            "customer_name": ticket.customertransid.custname if ticket.customertransid else None,
            "company_name": ticket.companytransid.companyname if ticket.companytransid else None,
        },
        "activities": [],
        "notes": [],
        "timespent": []  # Initialize timespent array
    }

    # Add the current activity to the ticket's activities list
    for activity in activities:
        grouped_data["activities"].append({
            "transid": activity.transid,
            "activitydatetime": activity.activitydatetime,
            "tickettransid": activity.tickettransid.transid,
            "activitydoneby": activity.activitydoneby if activity.activitydoneby else None,
            "creatorcode": activity.creatorcode if activity.creatorcode else None,
            "entry_date": activity.entry_date,
            "update_date": activity.update_date,
            "activity_message": activity.activity_message if activity.activity_message else "No activity message provided.",
            "activitytype": activity.activitytype if activity.activitytype else "No activity type provided.",
        })

    # Fetch and add notes for the ticket
    notes = QitTicketnotes.objects.filter(tickettransid=ticket).order_by('-notesdate', '-notestime')
    for note in notes:
        base64_encoded_file = None
        if note.notesattachedfile:
            try:
                base64_encoded_file = base64.b64encode(note.notesattachedfile).decode('utf-8')
            except Exception:
                base64_encoded_file = None
        if note.companytransid:
            userrole = "Company"
            creator_transid = note.companytransid.transid  # Get the company transid
        elif note.usertransid:
            userrole = "Company User"
            creator_transid = note.usertransid.transid  # Get the company user transid
        elif note.custtransid:
            userrole = "Customer"
            creator_transid = note.custtransid.transid  # Get the customer transid
        else:
            userrole = "Unknown"
            creator_transid = None  # No transid if the user is unknown

        grouped_data["notes"].append({
            "notesattachedfile": note.notesattachedfile,
            "notesdate": note.notesdate,
            "notestime": note.notestime,
            "notescreatedby": note.notescreatedby,
            "notesdescription": note.notesdescription,
            "userrole": userrole,
            "creator_transid": creator_transid,  # Add creator_transid here
        })

    # Add timespent data to the response and replace usertransid with activitydoneby
    for time in timespent:
        activitydoneby = None
        userrole = "Unknown"

        if time.usertransid:
            activitydoneby = time.usertransid.cmpuserusername
            userrole = "Company User"
        elif time.companytransid:
            activitydoneby = time.companytransid.companyname
            userrole = "Company"
        elif time.customertransid:
            activitydoneby = time.customertransid.custname
            userrole = "Customer"

        formatted_start_date = time.start_date.strftime('%d-%m-%Y') if time.start_date else None
        formatted_update_date = time.update_date.strftime('%d-%m-%Y') if time.update_date else None

        updated_by = activitydoneby

        grouped_data["timespent"].append({
            "transid": time.transid,
            "starttime": time.starttime,
            "endtime": time.endtime,
            "currentdate": time.currentdate,
            "description": time.description,
            "tickettransid": time.tickettransid.transid,
            "activitydoneby": activitydoneby,
            "userrole": userrole,
            "update_date": time.update_date,
            "start_date": formatted_start_date,
            "updated_by": updated_by, 
        })

    # Return the grouped data as a response
    return Response(grouped_data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])
def ticket_activities_list(request):
    # Fetch all ticket activities with related data
    activities = QitActivities.objects.select_related(
        'tickettransid__ticketcategorytransid',
        'tickettransid__ticketsubcattransid',
        'tickettransid__companytransid',
        'tickettransid__customertransid',
        'tickettransid__usertransid'
    ).all()

    # Group data by ticketcode
    grouped_data = {}

    for activity in activities:
        ticket = activity.tickettransid
        ticketcode = ticket.ticketcode

        # Initialize ticket data if not already in the grouped data
        if ticketcode not in grouped_data:
            grouped_data[ticketcode] = {
                "message": f"Activities retrieved for ticket '{ticketcode}'.",
                "ticket": {
                    "ticketcode": ticket.ticketcode,
                    "ticketstatus": ticket.ticketstatus,
                    "ticketpriority": ticket.ticketpriority,
                    "ticketsubject": ticket.ticketsubject,
                    "ticketcategoryname": ticket.ticketcategorytransid.ticketcategoryname if ticket.ticketcategorytransid else None,
                    "ticketsubcatname": ticket.ticketsubcattransid.ticketsubcatname if ticket.ticketsubcattransid else None,
                    "customer_name": ticket.customertransid.custname if ticket.customertransid else None,
                    "company_name": ticket.companytransid.companyname if ticket.companytransid else None,
                },
                "activities": [],
                "notes": []
            }

        # Add the current activity to the ticket's activities list
        activity_message = (
            f"Activity type '{activity.activitytype}' performed."
            if activity.activitytype else "No specific activity type provided."
        )
        grouped_data[ticketcode]["activities"].append({
            "transid": activity.transid,
            "activitydatetime": activity.activitydatetime,
            "tickettransid": activity.tickettransid.transid,
            "activitydoneby": activity.activitydoneby,
            "creatorcode": activity.creatorcode if activity.creatorcode else None,
            "entry_date": activity.entry_date,
            "update_date": activity.update_date,
            "activity_message": activity_message,
        })

    # Fetch and add notes for each ticket
    for ticketcode, ticket_data in grouped_data.items():
        ticket = QitTickets.objects.get(ticketcode=ticketcode)  # Assuming QitTickettrans is the ticket model

        notes = QitTicketnotes.objects.filter(tickettransid=ticket).order_by('-notesdate', '-notestime')
        for note in notes:
            notesattachedfile = None
            if note.notesattachedfile:
                try:
                    with open(note.notesattachedfile, "rb") as file:
                        notesattachedfile = base64.b64encode(file.read()).decode('utf-8')
                except Exception as e:
                    notesattachedfile = None  # If there is an error, set to None

            ticket_data["notes"].append({
                "notesattachedfile": notesattachedfile,
                "notesdate": note.notesdate,
                "notestime": note.notestime,
                "notescreatedby": note.notescreatedby,
            })

    # Convert grouped data to a list for response
    response_data = list(grouped_data.values())

    return Response(response_data, status=status.HTTP_200_OK)

