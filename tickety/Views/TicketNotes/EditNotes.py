from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTicketnotes, QitTickets, QitCompanycustomer, QitCompanyuser,QitActivities,QitCompany
from tickety.serializers import QitTicketnotesSerializer
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
import json
from django.utils.timezone import now
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, authentication_classes, permission_classes
import base64
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.shortcuts import get_object_or_404
import os
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.test import APIClient  # Import APIClient for making API calls


@api_view(['PUT'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def edit_QitTicketnotes(request, transid):
    """
    Edit an existing ticket note, update the associated activity record,
    and group notes by ticket code.
    """
    # Extract data from the request
    ticket_code = request.data.get('ticketcode')  # Ticket code from the request
    notes_description = request.data.get('notesdescription')
    notes_file_base64 = request.data.get('notesattachedfile')
    usercode = request.data.get('cmpusercode')  # User code
    notes_date = request.data.get('notesdate') or timezone.now().date().isoformat()  # Default to today's date
    notes_time = request.data.get('notestime') or timezone.now().time().strftime('%H:%M:%S')  # Default to current time

    # Convert notes_date to a datetime.date object
    try:
        notes_date = datetime.strptime(notes_date, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Expected format: YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

    # Decode notes_file if provided
    notes_file = None
    if notes_file_base64:
        try:
            notes_file = base64.b64decode(notes_file_base64)
        except Exception:
            return Response({'error': 'Invalid base64 string for attached file'}, status=status.HTTP_400_BAD_REQUEST)

    # Get user by usercode
    try:
        user = QitCompanyuser.objects.get(cmpusercode=usercode)
        notes_created_by = user.cmpuserusername
    except QitCompanyuser.DoesNotExist:
        return Response({'error': 'User not found for the provided cmpusercode'}, status=status.HTTP_404_NOT_FOUND)

    # Get the note to be edited
    note = get_object_or_404(QitTicketnotes, transid=transid)

    # Update the note fields
    if notes_description:
        note.notesdescription = notes_description
    if notes_file:
        note.notesattachedfile = notes_file
    note.notesdate = notes_date
    note.notestime = notes_time
    note.notescreatedby = notes_created_by
    note.save()

    # Reflect changes in activities
    activity_datetime = timezone.make_aware(
        datetime.combine(notes_date, datetime.strptime(notes_time, '%H:%M:%S').time())
    )
    activity = QitActivities.objects.filter(tickettransid=note.tickettransid).last()  # Get the last activity for the ticket
    if activity:
        activity.activitydatetime = activity_datetime
        activity.activitydoneby = notes_created_by
        activity.activity_message = f"Note updated with description: {notes_description}"
        activity.save()

    # Group notes by ticket code
    grouped_notes = []
    ticket_notes = QitTicketnotes.objects.filter(tickettransid__ticketcode=ticket_code)

    for ticket_note in ticket_notes:
        grouped_notes.append({
            "ticketcode": ticket_note.tickettransid.ticketcode,
            "notesdescription": ticket_note.notesdescription,
            "notesattachedfile": base64.b64encode(ticket_note.notesattachedfile).decode('utf-8') if ticket_note.notesattachedfile else None,
            "notesdate": ticket_note.notesdate.isoformat(),
            "notestime": ticket_note.notestime,
            "notescreatedby": ticket_note.notescreatedby,
        })

    # Prepare the response
    response_data = {
        "message": "Note updated successfully!",
        "grouped_notes": grouped_notes,
        "updated_activity": {
            "transid": activity.transid if activity else None,
            "activitydatetime": activity.activitydatetime if activity else None,
            "activitydoneby": activity.activitydoneby if activity else None,
            "creatorcode": activity.creatorcode if activity else None,
            "activity_message": activity.activity_message if activity else None
        }
    }

    return Response(response_data, status=status.HTTP_200_OK)

