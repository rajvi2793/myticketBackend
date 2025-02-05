from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitConfiguration
from tickety.serializers import QitConfigurationSerializer
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views


@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def create_configuration(request):
    """
    Create or update a QitConfiguration record.
    """
    company_transid = request.data.get("company_transid")
    primary_email = request.data.get("primary_email")
    alt_email = request.data.get("alt_email")

    # Validate input
    if not company_transid or not primary_email:
        return Response(
            {"message": "Company ID and Primary Email are required fields."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Check if a configuration already exists for the given company
        configuration = QitConfiguration.objects.filter(company_transid=company_transid).first()
        if configuration:
            # Update the existing configuration
            configuration.primary_email = primary_email
            configuration.alt_email = alt_email
            configuration.save()
            return Response(
                {"message": "Configuration updated successfully!", "data": {
                    "company_transid": configuration.company_transid.transid,
                    "primary_email": configuration.primary_email,
                    "alt_email": configuration.alt_email
                }},
                status=status.HTTP_200_OK
            )
        else:
            # Create a new configuration
            serializer = QitConfigurationSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"message": "Configuration created successfully!", "data": serializer.data},
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {"message": "Invalid data provided", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        return Response(
            {"message": f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

   