from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitNotifications
from tickety.serializers import QitNotificationsSerializer,NotificationStatusUpdateSerializer  # Ensure you have a serializer for QitNotifications
from tickety.Views import auth_views

# @api_view(['GET'])
# @authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
# def get_notifications(request):
#     """
#     Retrieve notifications based on filters.
#     If `companytransid` is provided, it retrieves all notifications for a specific company.
#     """
#     # Query parameters
#     user_transid = request.query_params.get('usertransid')  # Filter by user
#     customer_transid = request.query_params.get('customertransid')  # Filter by customer
#     company_transid = request.query_params.get('companytransid')  # Filter by company
#     notification_type = request.query_params.get('notificationtype')  # Optional filter by type
#     notification_status = request.query_params.get('notificationstatus')  # Optional filter by status

#     # Ensure at least `companytransid` is provided
#     if not company_transid:
#         return Response(
#             {"message": "companytransid is required to retrieve company-specific notifications."},
#             status=status.HTTP_400_BAD_REQUEST
#         )

#     # Build a query filter dynamically based on provided parameters
#     filters = {'companytransid': company_transid}  # Filter by company ID (mandatory)
#     if user_transid:
#         filters['usertransid'] = user_transid
#     if customer_transid:
#         filters['customertransid'] = customer_transid
#     if notification_type:
#         filters['notificationtype__icontains'] = notification_type  # Partial match for type
#     if notification_status:
#         filters['notificationstatus__icontains'] = notification_status  # Partial match for status

#     try:
#         # Retrieve filtered notifications
#         notifications = QitNotifications.objects.filter(**filters).order_by('-entrydate')
#         serializer = QitNotificationsSerializer(notifications, many=True)
        
#         return Response(
#             {'message': 'Notifications retrieved successfully!', 'data': serializer.data},
#             status=status.HTTP_200_OK
#         )
#     except Exception as e:
#         return Response(
#             {'message': f"An error occurred: {str(e)}"},
#             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#         )

@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_notifications(request):
    """
    Retrieve notifications based on filters.
    If `companytransid` is provided, it retrieves all notifications for a specific company.
    If `customertransid` is also provided, it retrieves only notifications for that specific customer within the company.
    """
    # Query parameters
    user_transid = request.query_params.get('usertransid')  # Filter by user
    customer_transid = request.query_params.get('customertransid')  # Filter by customer
    company_transid = request.query_params.get('companytransid')  # Filter by company
    notification_type = request.query_params.get('notificationtype')  # Optional filter by type
    notification_status = request.query_params.get('notificationstatus')  # Optional filter by status

    # Ensure at least `companytransid` is provided
    if not company_transid:
        return Response(
            {"message": "companytransid is required to retrieve company-specific notifications."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Build a query filter dynamically based on provided parameters
    filters = {'companytransid': company_transid}  # Mandatory filter by company ID
    
    # Only add customertransid filter if it's provided and not 'undefined'
    if customer_transid and customer_transid != "undefined":
        filters['customertransid'] = customer_transid  # Restrict to specific customer within the company
    
    if user_transid:
        filters['usertransid'] = user_transid
    if notification_type:
        filters['notificationtype__icontains'] = notification_type  # Partial match for type
    if notification_status:
        filters['notificationstatus__icontains'] = notification_status  # Partial match for status

    try:
        # Retrieve filtered notifications
        notifications = QitNotifications.objects.filter(**filters).order_by('-entrydate')
        
        if not notifications.exists():
            return Response(
                {"message": "No notifications found for the given filters."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = QitNotificationsSerializer(notifications, many=True)
        
        return Response(
            {'message': 'Notifications retrieved successfully!', 'data': serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'message': f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

