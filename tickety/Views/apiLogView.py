from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitApilog
from datetime import datetime
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views

@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def get_all_apilogs(request):
    """
    API to retrieve all API logs, with optional filtering by `cmptransid`.
    """
    try:
        # Retrieve `cmptransid` from query parameters for filtering
        cmptransid = request.query_params.get('cmptransid')

        # Filter API logs based on `cmptransid` if provided
        if cmptransid:
            apilogs = QitApilog.objects.filter(cmptransid=cmptransid)
        else:
            apilogs = QitApilog.objects.all()

        # Prepare the logs as a list of dictionaries
        logs_data = [
            {
                "transid": log.transid,
                "module": log.module,
                "viewname": log.viewname,
                "methodname": log.methodname,
                "loglevel": log.loglevel,
                "logmessage": log.logmessage,
                "jsonpayload": log.jsonpayload,
                "loginuser": log.loginuser,
                "userrole": log.userrole,
                "entrydate": log.entrydate.strftime('%Y-%m-%d %H:%M:%S'),
                "cmptransid": log.cmptransid,
            }
            for log in apilogs
        ]

        return Response(
            {'message': 'API logs retrieved successfully', 'data': logs_data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'message': 'Failed to retrieve API logs', 'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
