from rest_framework import serializers
import base64
from tickety.models import QitUserlogin,QitTickets,QitTicketcategory,QitTicketsubcategory,QitTicketnotes,QitTickettimespent,QitCompanycustomer,QitCompanyuser,QitCompany,QitActivities,QitNotifications,QitConfiguration
from django.contrib.auth.hashers import make_password
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils.encoding import force_bytes
from django.core.files.base import ContentFile


class QIT_CompanyTBSerializer(serializers.ModelSerializer):
    companyavatar = serializers.CharField(required=False)
    class Meta:
        model = QitCompany
        fields = '__all__'

    def validate_companyemail(self, value):
        if QitCompany.objects.filter(companyemail=value).exists():
            raise serializers.ValidationError("Email already exists in the company records.")
        return value

    def validate(self, data):
        email = data.get('companyemail')
        password = data.get('companypassword')

        if QitCompany.objects.filter(companyemail=email, companypassword=password).exists():
            raise serializers.ValidationError(f"Email and password combination already exists in company records.")
        
        return data

    def create(self, validated_data):
        # Check if companyavatar is provided and handle the base64 string if present
        companyavatar = validated_data.get('companyavatar', None)
        if companyavatar:
            try:
                # Convert the base64 string to bytes
                avatar_data = base64.b64decode(companyavatar)
                validated_data['companyavatar'] = avatar_data  # Save the binary data in the database
            except (TypeError, ValueError):
                raise serializers.ValidationError("Invalid base64 string for companyavatar.")

        # Hash the password before saving
        password = validated_data.get('companypassword')
        if password:
            validated_data['companypassword'] = make_password(password)
        
        return super().create(validated_data)

    
class QIT_CompanyCustomerTBSerializer(serializers.ModelSerializer):
    # isotpverified = serializers.SerializerMethodField()

    class Meta:
        model = QitCompanycustomer
        fields = '__all__'
        extra_kwargs = {'custcode': {'required': False}}

    def validate_show_working_hrs(self, value):
        if value not in ['Yes', 'No', None]:
            raise serializers.ValidationError("Invalid value for show_working_hrs. Must be 'Yes' or 'No'.")
        return value

    def validate_custgstno(self, value):
        if value and len(value) != 12:
            raise serializers.ValidationError("GST number must be exactly 12 characters long.")
        return value

    def validate(self, data):
        email = data.get('custemail')
        password = data.get('custpassword')

        if QitCompanycustomer.objects.filter(custemail=email, custpassword=password ,custisdeleted=0).exists():
            raise serializers.ValidationError("Email and password combination already exists in customer records.")
        
        if QitCompany.objects.filter(companyemail=email).exists():
            raise serializers.ValidationError(f"Email {email} already exists in the company records.")
        
        if QitCompanyuser.objects.filter(cmpuseremail=email,cmpuserisdeleted=0).exists():
            raise serializers.ValidationError(f"Email {email} already exists in the company user records.")

        # Validate base64 data for custlogo
        if 'custlogo' in data:
            base64_logo = data['custlogo']
            try:
                base64.b64decode(base64_logo)  # Check if the base64 data is valid
            except base64.binascii.Error:
                raise serializers.ValidationError("Invalid base64 data for custlogo.")
        
        return data

    def create(self, validated_data):
        # Decode base64 custlogo if present
        if 'custlogo' in validated_data:
            base64_logo = validated_data.pop('custlogo')
            validated_data['custlogo'] = base64.b64decode(base64_logo)

        # Hash the password if present
        password = validated_data.get('custpassword')
        if password:
            validated_data['custpassword'] = make_password(password)

        # Generate a unique code if not provided
        if 'custcode' not in validated_data:
            validated_data['custcode'] = QitCompanycustomer().generate_code()

        return super().create(validated_data)


class QIT_CompanyUserTBSerializer(serializers.ModelSerializer):

    class Meta:
        model = QitCompanyuser
        fields = '__all__'
        extra_kwargs = {'cmpusercode': {'required': False}}  # Ensure that cmpusercode is not required

        def validate(self, data):
            email = data.get('cmpuseremail')
            password = data.get('cmpuserpassword')

            # Check if the email-password combination already exists in active users
            if QitCompanyuser.objects.filter(cmpuseremail=email, cmpuserpassword=password, cmpuserisdeleted=0).exists():
                raise serializers.ValidationError("Email and password combination already exists in user records.")

            # Check if email exists in QitCompany
            if QitCompany.objects.filter(companyemail=email).exists():
                raise serializers.ValidationError(f"Email {email} already exists in the company records.")

            # Check if email exists in QitCompanycustomer but is not deleted
            if QitCompanycustomer.objects.filter(custemail=email, custisdeleted=0).exists():
                raise serializers.ValidationError(f"Email {email} already exists in active customer records.")

            # Allow email reuse if customer is logically deleted (custisdeleted=1)
            return data

    # def validate(self, data):
    #     # Same email-password validation logic
    #     email = data.get('cmpuseremail')
    #     password = data.get('cmpuserpassword')

    #     if QitCompanyuser.objects.filter(cmpuseremail=email, cmpuserpassword=password).exists():
    #         raise serializers.ValidationError("Email and password combination already exists in user records.")

    #     # Check if email exists in other tables
    #     if QitCompany.objects.filter(companyemail=email).exists():
    #         raise serializers.ValidationError(f"Email {email} already exists in the company records.")
        
    #     if QitCompanycustomer.objects.filter(custemail=email).exists():
    #         raise serializers.ValidationError(f"Email {email} already exists in the customer records.")

    #     return data
    
    def create(self, validated_data):
        # Check if 'userlogo' is in the validated data
        userlogo_base64 = validated_data.get('userlogo', None)
        if userlogo_base64:
            try:
                # Decode the base64 string to binary
                decoded_file = base64.b64decode(userlogo_base64)
                validated_data['userlogo'] = decoded_file  # Set the decoded file data
            except base64.binascii.Error:
                raise serializers.ValidationError("Invalid base64 data for userlogo.")

        # Hash the password before saving
        password = validated_data.get('cmpuserpassword')
        if password:
            validated_data['cmpuserpassword'] = make_password(password)

        # Automatically generate the cmpusercode if not provided
        if 'cmpusercode' not in validated_data:
            validated_data['cmpusercode'] = QitCompanyuser().generate_code()

        return super().create(validated_data)


class QitUserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6, min_length=6)

    def validate_otp(self, value):
        # Ensure that the OTP is numeric
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric.")
        return value
    

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6, min_length=6)
    new_password = serializers.CharField(
        required=True, min_length=8, write_only=True, style={'input_type': 'password'}
    )

    def validate_new_password(self, value):
        # Ensure the password is strong (e.g., at least one number and one special character)
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        return value
    

class QitTicketcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QitTicketcategory
        fields = '__all__'

    def validate(self, data):
        category_name = data.get('ticketcategoryname')

        if QitTicketcategory.objects.filter(ticketcategoryname=category_name).exists():
            raise serializers.ValidationError({"error": ["This category already exists in records."]})
        
        return data

class QitTicketsubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QitTicketsubcategory
        fields = '__all__'

    def validate(self, data):
        subcategory_name = data.get('ticketsubcatname')

        if QitTicketsubcategory.objects.filter(ticketsubcatname=subcategory_name).exists():
            raise serializers.ValidationError({"error": ["This subcategory already exists in records."]})
        
        return data

class QitTicketsSerializer(serializers.ModelSerializer):
    customer_name = serializers.SerializerMethodField()
    username = serializers.SerializerMethodField()
    working_user = serializers.SerializerMethodField()
    ticketcategoryname = serializers.SerializerMethodField()
    ticketsubcatname = serializers.SerializerMethodField()
    timespent = serializers.SerializerMethodField()
    show_working_hrs = serializers.SerializerMethodField()  # Add this field

    class Meta:
        model = QitTickets
        fields = '__all__'  # Include all fields from the model
        extra_kwargs = {
            'ticketcode': {'required': False},
            'entry_date': {'read_only': True},
            'update_date': {'read_only': True},
        }

    def get_working_user(self, obj):
        latest_activity = QitActivities.objects.filter(tickettransid=obj).order_by('-activitydatetime').first()
        return latest_activity.activitydoneby if latest_activity else None

    def get_customer_name(self, obj):
        if obj.customertransid:
            return obj.customertransid.custname
        return None

    def get_username(self, obj):
        if obj.usertransid:
            return obj.usertransid.cmpuserusername
        return None

    def get_ticketcategoryname(self, obj):
        if obj.ticketcategorytransid:
            return obj.ticketcategorytransid.ticketcategoryname
        return None

    def get_ticketsubcatname(self, obj):
        if obj.ticketsubcattransid:
            return obj.ticketsubcattransid.ticketsubcatname
        return None

    def get_timespent(self, obj):
        timespent_entries = QitTickettimespent.objects.filter(tickettransid=obj)
        return [
            {
                "starttime": timespent.starttime,
                "endtime": timespent.endtime,
                "description": timespent.description,
            }
            for timespent in timespent_entries
        ]

    def get_show_working_hrs(self, obj):
        # Access the related QitCompanycustomer and fetch the show_working_hrs field
        if obj.customertransid:
            return obj.customertransid.show_working_hrs
        return None

    def create(self, validated_data):
        if 'ticketcode' not in validated_data or not validated_data['ticketcode']:
            ticket = QitTickets()
            ticket.ticketcode = ticket.generate_ticketcode()
            validated_data['ticketcode'] = ticket.ticketcode
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'ticketcode' not in validated_data or not validated_data['ticketcode']:
            validated_data['ticketcode'] = instance.generate_ticketcode()
        return super().update(instance, validated_data)
    

class QitTicketnotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QitTicketnotes
        fields = '__all__'

    def create(self, validated_data):
        # Handle base64 data for notesattachedfile (if any)
        if 'notesattachedfile' in validated_data:
            base64_file = validated_data.pop('notesattachedfile')  # Get the base64 string

            try:
                # Decode the base64 string to binary
                decoded_file = base64.b64decode(base64_file)
                validated_data['notesattachedfile'] = decoded_file  # Set the decoded file data
            except base64.binascii.Error:
                raise serializers.ValidationError("Invalid base64 data for notesattachedfile.")

        # Fetch customer or user details for `ticketcreatedby`
        customer_id = validated_data.get('customertransid')
        user_id = validated_data.get('usertransid')
        # ticketcreatedby = None

        if customer_id:
            # Fetch the customer's name
            try:
                customer = QitCompanycustomer.objects.get(transid=customer_id.transid)
                # ticketcreatedby = customer.custname  # Replace `customer_name` with the appropriate field
            except QitCompanycustomer.DoesNotExist:
                raise serializers.ValidationError({'customertransid': 'Customer does not exist.'})

        if user_id:
            # Fetch the user's name
            try:
                user = QitCompanyuser.objects.get(transid=user_id.transid)
                # ticketcreatedby = user.cmpuserusername  # Replace `username` with the appropriate field
            except QitCompanyuser.DoesNotExist:
                raise serializers.ValidationError({'usertransid': 'User does not exist.'})

        # Call the parent class's create method to save the data
        return super().create(validated_data)


class QitTicketTimeSpentSerializer(serializers.ModelSerializer):
    class Meta:
        model = QitTickettimespent
        fields = '__all__'

    def to_representation(self, instance):
        # Get the default serialized data
        data = super().to_representation(instance)
        
        # Format the start_date if it exists
        if instance.start_date:
            data['start_date'] = instance.start_date.strftime('%d-%m-%Y')
        
        return data

    # Optional validation or custom behavior for entry_date and update_date
    def validate_entry_date(self, value):
        # Custom validation if needed
        return value

    def validate_update_date(self, value):
        # Custom validation if needed
        return value
    
class PasswordReqUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    type = serializers.CharField(max_length=50)


class ToggleTicketStatusSerializer(serializers.Serializer):
    ticketcode = serializers.CharField(required=True, max_length=50)
    isStatus = serializers.ChoiceField(choices=["Open", "Work in progress", "Escalated", "Solved"])
    creatorcode = serializers.CharField(max_length=50, required=False)

    def to_internal_value(self, data):
        """
        Override to normalize the 'isStatus' field value to match database enum values
        """
        if 'isStatus' in data:
            # Normalize status to lowercase to match enum format and replace as needed
            status_mapping = {
                "open": "Open",
                "work in progress": "Work in progress",
                "escalated": "Escalated",
                "solved": "Solved",
            }
            normalized_status = data['isStatus'].strip().lower()
            if normalized_status in status_mapping:
                data['isStatus'] = status_mapping[normalized_status]
            else:
                raise serializers.ValidationError(
                    {"isStatus": [f"'{data['isStatus']}' is not a valid choice."]}
                )

        return super().to_internal_value(data)

class QitActivitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = QitActivities
        fields = ['transid', 'activitydatetime', 'tickettransid', 'activitydoneby', 'creatorcode', 'entry_date', 'update_date']


class QitActivitiesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QitActivities
        fields = ['transid', 'activitydatetime', 'tickettransid', 'activitydoneby', 'creatorcode', 'entry_date', 'update_date']

    def create(self, validated_data):
        creatorcode = validated_data.get('creatorcode')
        
        # Check if the creatorcode exists in QitCompanyUser
        activitydoneby = None
        try:
            user = QitCompanyuser.objects.get(cmpusercode=creatorcode)
            activitydoneby = user.cmpuserusername  # Assuming `username` field exists in QitCompanyUser
        except QitCompanyuser.DoesNotExist:
            pass  # Continue to check QitCompanyCustomer
        
        if not activitydoneby:
            try:
                customer = QitCompanycustomer.objects.get(custcode=creatorcode)
                activitydoneby = customer.custname  # Assuming `username` field exists in QitCompanyCustomer
            except QitCompanycustomer.DoesNotExist:
                raise ValidationError(f"Invalid creator code: {creatorcode}")

        validated_data['activitydoneby'] = activitydoneby
        
        # Create the new activity
        activity = QitActivities.objects.create(**validated_data)
        
        # Return the created activity with all fields
        return activity
    

class QitNotificationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = QitNotifications
        fields = '__all__'  # Include all fields or specify the required ones

class NotificationStatusUpdateSerializer(serializers.Serializer):
    transid = serializers.IntegerField()  # The ID of the notification
    notificationstatus = serializers.ChoiceField(choices=['read', 'unread'])  # The new status to be set

class QitConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QitConfiguration
        fields = ['company_transid', 'primary_email', 'alt_email']

    def validate_primary_email(self, value):
        """Validate that the primary email is valid."""
        if not value or '@' not in value:
            raise serializers.ValidationError("Please provide a valid primary email address.")
        return value

    def validate_alt_email(self, value):
        """Validate that the alternate email is valid."""
        if value and '@' not in value:
            raise serializers.ValidationError("Please provide a valid alternate email address.")
        return value