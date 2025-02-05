from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitNotifications
from tickety.serializers import QitNotificationsSerializer,NotificationStatusUpdateSerializer  # Ensure you have a serializer for QitNotifications
from tickety.Views import auth_views


@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def update_notification_status(request):
    # Validate input data using the serializer
    serializer = NotificationStatusUpdateSerializer(data=request.data)
    if serializer.is_valid():
        # Extract transid and notificationstatus from the validated data
        transid = serializer.validated_data['transid']
        notificationstatus = serializer.validated_data['notificationstatus']

        # Get the notification by transid
        try:
            notification = QitNotifications.objects.get(transid=transid)
            # Update the notification status
            notification.notificationstatus = notificationstatus
            notification.save()

            return Response({"message": "Notification status updated successfully."}, status=status.HTTP_200_OK)
        except QitNotifications.DoesNotExist:
            return Response({"error": "Notification not found."}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
