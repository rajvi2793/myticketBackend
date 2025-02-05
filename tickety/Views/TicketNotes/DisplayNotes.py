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

@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_all_ticket_notes(request):
    try:
        ticket_notes = QitTicketnotes.objects.all()

        # Serialize the ticket notes
        serializer = QitTicketnotesSerializer(ticket_notes, many=True)

        return Response({"message": "Ticket notes fetched successfully!", "status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": str(e), "status": "error"}, status=status.HTTP_400_BAD_REQUEST)
