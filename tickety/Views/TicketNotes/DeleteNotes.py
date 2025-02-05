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

@api_view(['DELETE'])
# @authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def delete_QitTicketnote(request, transid):
    """
    Delete a ticket note and its associated activity by transid.
    """
    try:
        # Fetch the note to delete
        note = QitTicketnotes.objects.get(transid=transid)

        # Delete associated activity (if any)
        QitActivities.objects.filter(tickettransid=note.tickettransid, activitydoneby=note.notescreatedby).delete()

        # Delete the note
        note.delete()

        return Response({"message": f"Ticket note with TransId {transid} deleted successfully!"}, status=status.HTTP_200_OK)
    except QitTicketnotes.DoesNotExist:
        return Response({"error": f"Ticket note with TransId {transid} not found."}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

