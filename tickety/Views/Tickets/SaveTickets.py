from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from tickety.models import QitTickets, QitTicketcategory, QitTicketsubcategory, QitCompany, QitCompanycustomer, QitCompanyuser,QitActivities,QitNotifications,QitConfiguration
from tickety.serializers import QitTicketcategorySerializer, QitTicketsSerializer, QitTicketsubcategorySerializer,ToggleTicketStatusSerializer,QitActivitiesSerializer,QitNotificationsSerializer
from rest_framework.views import APIView
from rest_framework.decorators import authentication_classes
from tickety.Views import auth_views
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@authentication_classes([auth_views.CustomAuthentication])  # Apply custom authentication
def save_ticket(request):
    """Save a new ticket with category and optional subcategory validation."""
    ticket_category = request.data.get('ticketcategorytransid')  # Retrieve category ID
    ticket_subcategory = request.data.get('ticketsubcattransid')  # Retrieve subcategory ID (optional)
    ticket_company = request.data.get('companytransid')  # Retrieve company ID
    ticket_customer = request.data.get('customertransid')  # Retrieve customer ID
    ticket_user = request.data.get('usertransid')  # Retrieve user ID
    ticket_created_by = str(request.data.get('ticketcreatedby', ""))  # Convert to string to avoid errors
    ticketsubject=request.data.get('ticketsubject')
    ticketattachedfile=request.data.get('ticketattachedfile')

    print(ticketattachedfile)

    # Check if customertransid, usertransid, or companytransid is provided
    if not ticket_customer and not ticket_user and not ticket_company:
        return Response({'error': 'You must provide either customertransid, usertransid, or companytransid.'}, 
                        status=status.HTTP_400_BAD_REQUEST)

    # Check if the category exists
    try:
        category = QitTicketcategory.objects.get(pk=ticket_category)
    except QitTicketcategory.DoesNotExist:
        return Response({'error': 'Ticket Category does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

    # Subcategory validation is optional
    subcategory = None
    if ticket_subcategory:
        try:
            subcategory = QitTicketsubcategory.objects.get(pk=ticket_subcategory)
        except QitTicketsubcategory.DoesNotExist:
            pass  # Skip validation error for subcategory

    # Check if the company exists
    try:
        company = QitCompany.objects.get(pk=ticket_company)
    except QitCompany.DoesNotExist:
        return Response({'error': 'Company does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the customer exists
    try:
        customer = QitCompanycustomer.objects.get(pk=ticket_customer)
    except QitCompanycustomer.DoesNotExist:
        return Response({'error': 'Customer does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user exists if usertransid is provided
    if ticket_user:
        try:
            user = QitCompanyuser.objects.get(pk=ticket_user)
        except QitCompanyuser.DoesNotExist:
            return Response({'error': 'User does not exist!'}, status=status.HTTP_400_BAD_REQUEST)

    # Resolve 'ticketcreatedby' to customer, user, or company name
    if ticket_created_by:
        if ticket_created_by.startswith('customer'):  # Handle customer code
            try:
                customer = QitCompanycustomer.objects.get(custcode=ticket_created_by)
                ticket_created_by_name = customer.custname
            except QitCompanycustomer.DoesNotExist:
                return Response({'error': f'Customer with code {ticket_created_by} does not exist!'}, status=status.HTTP_400_BAD_REQUEST)
        elif ticket_created_by.startswith('user'):  # Handle user code
            try:
                user = QitCompanyuser.objects.get(cmpusercode=ticket_created_by)
                ticket_created_by_name = user.cmpuserusername
            except QitCompanyuser.DoesNotExist:
                return Response({'error': f'User with code {ticket_created_by} does not exist!'}, status=status.HTTP_400_BAD_REQUEST)
        elif ticket_created_by.isdigit():  # Handle company code
            try:
                company = QitCompany.objects.get(transid=int(ticket_created_by))
                ticket_created_by_name = company.companyname
            except QitCompany.DoesNotExist:
                return Response({'error': f'Company with transid {ticket_created_by} does not exist!'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid ticketcreatedby value!'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        ticket_created_by_name = "Unknown"

    # Prepare data for saving the ticket
    data = request.data
    data['ticketcategorytransid'] = category.transid  # Correct if 'transid' is the primary key
    data['ticketsubcattransid'] = subcategory.transid if subcategory else None  # Allow subcategory to be None
    data['companytransid'] = company.transid  # Same here for company
    data['customertransid'] = customer.transid  # Set customer
    data['usertransid'] = user.transid if ticket_user else None  # Set user if provided
    data['ticketcreatedby'] = ticket_created_by_name  # Set ticket created by name
    data['ticketsubject']=ticketsubject
    data['ticketattachedfile']=ticketattachedfile

    # Create ticket serializer and validate
    serializer = QitTicketsSerializer(data=data)
    if serializer.is_valid():
        ticket = serializer.save()  # Save the ticket

                # Add notification entry for the new ticket
        notification_data = {
            'title': f'New Ticket Created: [{ticket.ticketcode}]: {ticket.ticketsubject}',
            'description': ticket.ticketdescription,
            'notificationtype': 'Ticket',
            'notificationstatus': 'unread',  # Default status
            'usertransid': user if ticket_user else None,  # User ID
            'customertransid': customer,  # Customer ID
            'companytransid': company,  # Company ID
            'tickettransid': ticket,  # Related ticket
            'createdby': ticket_created_by_name,
            'entrydate': ticket.ticketdatetime,  # Use the ticket's datetime
        }
        QitNotifications.objects.create(**notification_data)

        # Now, add an activity for this ticket
        activity_entry = QitActivities.objects.create(
            tickettransid=ticket,
            activitytype="Ticket",
            activitydatetime=ticket.ticketdatetime,
            activitydoneby=ticket.ticketcreatedby,
            activity_message=f'New Ticket Created:{ticket.ticketsubject}',  # Use description as the activity message
        )

        # Attempt to retrieve email configuration, but make it optional
        primary_email = None
        alt_email = None
        try:
            configuration = QitConfiguration.objects.get(company_transid=company)
            primary_email = configuration.primary_email
            alt_email = configuration.alt_email
        except QitConfiguration.DoesNotExist:
            pass  # No configuration found; continue without email notifications

        # Collect all email recipients, including customer's email if provided
        email_recipients = []
        if primary_email:
            email_recipients.append(primary_email)
        if alt_email:
            email_recipients.append(alt_email)
        if ticket_customer:
            email_recipients.append(customer.custemail)  # Add customer's email

        # Send email notifications if recipients exist
        if email_recipients:
            email_subject = f"New Ticket Created: {ticket.ticketsubject}"
            html_message = render_to_string('TicketEmail.html', {
                'ticket_subject': ticket.ticketsubject,
                'ticket_description': ticket.ticketdescription,
                'ticket_created_by': ticket_created_by_name,
                'ticket_date': ticket.ticketdatetime.strftime('%d/%m/%Y'),
            })
            plain_message = strip_tags(html_message)
            try:
                send_mail(
                    subject=email_subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=email_recipients,
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send email: {str(e)}")

        return Response({'message': 'Ticket saved successfully!', 'data': serializer.data}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
