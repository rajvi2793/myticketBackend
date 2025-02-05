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

@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def save_QitTicketnotes(request):
    try:
        # Extract data from the request
        ticket_code = request.data.get('ticketcode')
        notes_description = request.data.get('notesdescription')
        notes_file_base64 = request.data.get('notesattachedfile')
        usercode = request.data.get('cmpusercode')
        custcode = request.data.get('custcode')
        companytransid = request.data.get('companytransid')
        notes_date = request.data.get('notesdate') or timezone.now().date().isoformat()
        notes_time = request.data.get('notestime') or timezone.now().time().strftime('%H:%M:%S')

        # Convert notes_date to a datetime.date object
        try:
            notes_date = datetime.strptime(notes_date, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': 'Invalid date format. Expected format: YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)

        # Decode the notes file if provided
        # notes_file = None
        # if notes_file_base64:
        #     try:
        #         notes_file = base64.b64decode(notes_file_base64)
        #     except Exception:
        #         return Response({'error': 'Invalid type attached file'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch user role and name
        notes_created_by = 'Unknown'
        userrole = None

        if usercode:
            try:
                user = QitCompanyuser.objects.get(cmpusercode=usercode)
                notes_created_by = user.cmpuserusername
                userrole = "companyuser"
            except QitCompanyuser.DoesNotExist:
                return Response({'error': 'User not found for the provided cmpusercode'}, status=status.HTTP_404_NOT_FOUND)

        if custcode:
            try:
                customer = QitCompanycustomer.objects.get(custcode=custcode)
                notes_created_by = customer.custname
                userrole = "customer"
            except QitCompanycustomer.DoesNotExist:
                return Response({'error': 'Customer not found for the provided custcode'}, status=status.HTTP_404_NOT_FOUND)

        if companytransid:
            try:
                company = QitCompany.objects.get(transid=companytransid)
                notes_created_by = company.companyname
                userrole = "company"
            except QitCompany.DoesNotExist:
                return Response({'error': 'Company not found for the provided companytransid'}, status=status.HTTP_404_NOT_FOUND)

        # Save the note
        note = QitTicketnotes.objects.create(
            tickettransid=QitTickets.objects.get(ticketcode=ticket_code),
            notesdescription=notes_description,
            notesattachedfile=notes_file_base64,
            notesdate=notes_date,
            notestime=notes_time,
            notescreatedby=notes_created_by,
            custtransid=QitCompanycustomer.objects.get(custcode=custcode) if custcode else None,
            companytransid=QitCompany.objects.get(transid=companytransid) if companytransid else None,
            usertransid=QitCompanyuser.objects.get(cmpusercode=usercode) if usercode else None
        )

        # Add a corresponding entry in QitActivities
        activity_entry = QitActivities.objects.create(
            tickettransid=note.tickettransid,
            activitytype="Note Added",
            activitydatetime=timezone.now(),
            activitydoneby=notes_created_by,
            creatorcode=usercode or custcode or companytransid,
            entry_date=notes_date,
            update_date=timezone.now(),
            activity_message=f"Notes Added for ticket: {ticket_code}.",
        )

        # Group notes by ticketcode with userrole
        grouped_notes = []
        ticket_notes = QitTicketnotes.objects.filter(tickettransid__ticketcode=ticket_code)

        for note in ticket_notes:
            # Determine userrole based on notescreatedby
            role = "unknown"
            if QitCompanyuser.objects.filter(cmpuserusername=note.notescreatedby).exists():
                role = "companyuser"
            elif QitCompanycustomer.objects.filter(custname=note.notescreatedby).exists():
                role = "customer"
            elif QitCompany.objects.filter(companyname=note.notescreatedby).exists():
                role = "company"

            grouped_notes.append({
                "ticketcode": note.tickettransid.ticketcode,
                "notesdescription": note.notesdescription,
                "notesattachedfile": note.notesattachedfile,
                "notesdate": note.notesdate.isoformat(),
                "notestime": note.notestime,
                "notescreatedby": note.notescreatedby,
                "userrole": role  # Include userrole in the response
            })

        return Response({
            "ticketcode": ticket_code,
            "notes": grouped_notes,
            "userrole": userrole,  # Include the role of the last saved note
            "activity": {
                "transid": activity_entry.transid,
                "activitytype": activity_entry.activitytype,
                "activitydatetime": activity_entry.activitydatetime,
                "activitydoneby": activity_entry.activitydoneby,
                "creatorcode": activity_entry.creatorcode,
                "activity_message": activity_entry.activity_message,
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


