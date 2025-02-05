from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitConfiguration
from tickety.serializers import QitConfigurationSerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views



@api_view(['GET'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def filter_configuration_by_company(request, company_transid):
    """
    Filter QitConfiguration records based on the provided company_transid.
    """
    try:
        # Get all configurations for the given company_transid
        configurations = QitConfiguration.objects.filter(company_transid=company_transid)
        
        if not configurations.exists():
            return Response(
                {"message": f"No configurations found for company_transid: {company_transid}"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Serialize the data
        serializer = QitConfigurationSerializer(configurations, many=True)
        
        return Response(
            {"message": "Configurations retrieved successfully", "data": serializer.data},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {"message": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

