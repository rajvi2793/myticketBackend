from django.db import models
from datetime import datetime
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import BaseUserManager
import string
import random
from django.db import transaction
from django.db.models import Max


class QitActivities(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.
    activitydatetime = models.DateTimeField(db_column='ActivityDateTime')  # Field name made lowercase.
    tickettransid = models.ForeignKey('QitTickets', models.DO_NOTHING, db_column='TicketTransId')  # Field name made lowercase.
    activitydoneby = models.CharField(db_column='ActivityDoneBy', max_length=255, blank=True, null=True)  # Field name made lowercase.  
    creatorcode = models.CharField(db_column='CreatorCode', max_length=50, blank=True, null=True)  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)
    activity_message = models.TextField(blank=True, null=True)
    activitytype = models.CharField(max_length=100, null=True, blank=True)

    
    class Meta:
        managed = False
        db_table = 'QIT_Activities'


class QitCompany(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=255)  # Field name made lowercase.
    companyemail = models.CharField(db_column='CompanyEmail', max_length=255)  # Field name made lowercase.
    companypassword = models.CharField(db_column='CompanyPassword', max_length=255)  # Field name made lowercase.
    companyavatar = models.BinaryField(db_column='CompanyAvatar', blank=True, null=True)  # Base64 image
    companyphno = models.CharField(db_column='CompanyPhno', max_length=15, blank=True, null=True)  # Field name made lowercase.
    companyisdeleted = models.IntegerField(db_column='CompanyIsDeleted')  # Field name made lowercase.
    companyaddress = models.CharField(db_column='CompanyAddress', max_length=255, blank=True, null=True)  # Field name made lowercase.  
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)
    companystatus = models.CharField(db_column='CompanyStatus', max_length=8, blank=True, null=True)  # Field name made lowercase.      
    isotpverified = models.CharField(max_length=1, blank=True, null=True)
    
    class Meta:
        managed = False
        db_table = 'QIT_Company'


class QitCompanycustomer(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.
    custcode = models.CharField(db_column='CustCode', unique=True, max_length=50)  # Field name made lowercase.
    custname = models.CharField(db_column='CustName', max_length=255)  # Field name made lowercase.
    custemail = models.CharField(db_column='CustEmail', max_length=255)  # Field name made lowercase.
    custpassword = models.CharField(db_column='CustPassword', max_length=255)  # Field name made lowercase.
    custphno = models.CharField(db_column='CustPhno', max_length=15, blank=True, null=True)  # Field name made lowercase.
    custstatus = models.CharField(db_column='CustStatus', max_length=8)  # Field name made lowercase.
    custtype = models.CharField(db_column='CustType', max_length=100, blank=True, null=True)  # Field name made lowercase.
    custgstno = models.CharField(db_column='CustGstNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    custregaddr = models.TextField(db_column='CustRegAddr', blank=True, null=True)  # Field name made lowercase.
    custcity = models.CharField(db_column='CustCity', max_length=100, blank=True, null=True)  # Field name made lowercase.
    custpincode = models.CharField(db_column='CustPinCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    custstate = models.CharField(db_column='CustState', max_length=100, blank=True, null=True)  # Field name made lowercase.
    custcountry = models.CharField(db_column='CustCountry', max_length=100, blank=True, null=True)  # Field name made lowercase.        
    custlogo = models.BinaryField(db_column='CustLogo', blank=True, null=True)  # Field name made lowercase.
    custisdeleted = models.IntegerField(db_column='CustIsDeleted')  # Field name made lowercase.
    companytransid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='CompanyTransId')  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)
    passwordreq = models.CharField(db_column='PasswordReq', max_length=255, blank=True, null=True)  # Field name made lowercase.        
    isotpverified = models.CharField(max_length=1, blank=True, null=True)
    show_working_hrs = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'QIT_CompanyCustomer'

    def generate_code(self):
        year = datetime.now().year
        role = 'customer'
        # Get the number of existing customers for the same year
        last_customer = QitCompanycustomer.objects.filter(custcode__startswith=f"{role}{year}").order_by('-custcode').first()
        suffix = 1
        if last_customer:
            last_suffix = int(last_customer.custcode[len(f"{role}{year}"):])
            suffix = last_suffix + 1

        # Generate random letter(s) between A-Z
        letters = ''.join(random.choices(string.ascii_uppercase, k=1))
        code = f"{role}{year}{letters}{suffix}"  # Removed the dash
        return code

    def save(self, *args, **kwargs):
        if not self.custcode:
            self.custcode = self.generate_code()  # Generate code before saving
        super(QitCompanycustomer, self).save(*args, **kwargs)



class QitCompanyuser(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.
    cmpusercode = models.CharField(db_column='CmpUserCode', unique=True, max_length=50)  # Field name made lowercase.
    cmpuseremail = models.CharField(db_column='CmpUserEmail', max_length=255)  # Field name made lowercase.
    cmpuserpassword = models.CharField(db_column='CmpUserPassword', max_length=255)  # Field name made lowercase.
    cmpuserusername = models.CharField(db_column='CmpUserUsername', max_length=255)  # Field name made lowercase.
    cmpusercontactnumber = models.CharField(db_column='CmpUserContactNumber', max_length=15, blank=True, null=True)  # Field name made lowercase.
    cmpuserstatus = models.CharField(db_column='CmpUserStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.     
    cmpuserisdeleted = models.IntegerField(db_column='CmpUserIsDeleted')  # Field name made lowercase.
    companytransid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='CompanyTransId')  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)
    passwordreq = models.CharField(db_column='PasswordReq', max_length=255, blank=True, null=True)  # Field name made lowercase.
    isotpverified = models.CharField(max_length=1, blank=True, null=True)
    userlogo = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'QIT_CompanyUser'

    def generate_code(self):
        # Generate usercode based on role and year
        year = datetime.now().year
        role = 'user'
        # Get the number of existing users for the same year
        last_user = QitCompanyuser.objects.filter(cmpusercode__startswith=f"{role}{year}").order_by('-cmpusercode').first()
        suffix = 1
        if last_user:
            # Extract the numeric part of the suffix (last 4 digits)
            last_suffix = int(last_user.cmpusercode[-4:])
            suffix = last_suffix + 1

        # Generate random letter(s) between A-Z
        letters = ''.join(random.choices(string.ascii_uppercase, k=1))
        code = f"{role}{year}{letters}{suffix:04d}"  # Role + year + letter + 4-digit suffix
        return code

    def save(self, *args, **kwargs):
        # If cmpusercode is not provided, generate it before saving
        if not self.cmpusercode:
            self.cmpusercode = self.generate_code()
        super(QitCompanyuser, self).save(*args, **kwargs)




class QitSuperadmintb(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.    
    email = models.CharField(db_column='Email', max_length=255)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=255)  # Field name made lowercase.    
    companyname = models.CharField(db_column='CompanyName', max_length=255)  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)

    class Meta:
        managed = False
        db_table = 'QIT_SuperAdminTB'


class QitTicketcategory(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.    
    ticketcategoryname = models.CharField(db_column='TicketCategoryName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    companytransid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='CompanyTransId')  # Field name made lowercase.
    ticketisdeleted = models.IntegerField(db_column='TicketIsDeleted')  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)

    class Meta:
        managed = False
        db_table = 'QIT_TicketCategory'


class QitTicketnotes(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.
    notesdescription = models.TextField(db_column='NotesDescription', blank=True, null=True)  # Field name made lowercase.
    notesattachedfile = models.TextField(db_column='NotesAttachedFile', blank=True, null=True)  # Field name made lowercase.
    notesdate = models.DateField(db_column='NotesDate', blank=True, null=True)  # Field name made lowercase.
    notestime = models.TimeField(db_column='NotesTime', blank=True, null=True)  # Field name made lowercase.
    notescreatedby = models.CharField(db_column='NotesCreatedBy', max_length=255, blank=True, null=True)  # Field name made lowercase.
    tickettransid = models.ForeignKey('QitTickets', models.DO_NOTHING, db_column='TicketTransId')  # Field name made lowercase.
    custtransid = models.ForeignKey(QitCompanycustomer, models.DO_NOTHING, db_column='CustTransId', blank=True, null=True)  # Field name made lowercase.
    usertransid = models.ForeignKey(QitCompanyuser, models.DO_NOTHING, db_column='UserTransId', blank=True, null=True)  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)
    activitytransid = models.ForeignKey(QitActivities, models.DO_NOTHING, db_column='ActivityTransId', blank=True, null=True)  # Field name made lowercase.
    companytransid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='CompanyTransId', blank=True, null=True)  # Field name made lowercase.    activitytransid = models.ForeignKey(QitActivities, models.DO_NOTHING, db_column='ActivityTransId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'QIT_TicketNotes'


class QitTicketsubcategory(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.    
    ticketsubcatname = models.CharField(db_column='TicketSubCatName', max_length=255)  # Field name made lowercase.
    ticketsubiddeleted = models.IntegerField(db_column='TicketSubIdDeleted')  # Field name made lowercase.
    companytransid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='CompanyTransId')  # Field name made lowercase.
    ticketcategorytransid = models.ForeignKey(QitTicketcategory, models.DO_NOTHING, db_column='TicketCategoryTransId')  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'QIT_TicketSubCategory'


class QitTickettimespent(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.    
    starttime = models.TimeField(db_column='StartTime')  # Field name made lowercase.
    endtime = models.TimeField(db_column='EndTime')  # Field name made lowercase.
    currentdate = models.DateField(db_column='CurrentDate')  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    tickettransid = models.ForeignKey('QitTickets', models.DO_NOTHING, db_column='TicketTransId')  # Field name made lowercase.
    usertransid = models.ForeignKey(QitCompanyuser, models.DO_NOTHING, db_column='UserTransId', null=True)  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)
    companytransid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='companytransid', blank=True, null=True)
    updated_by = models.CharField(max_length=255, blank=True, null=True)  # New field
    start_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'QIT_TicketTimeSpent'


class QitTickets(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.    
    ticketcode = models.CharField(db_column='TicketCode', unique=True, max_length=50)  # Field name made lowercase.
    ticketstatus = models.CharField(db_column='TicketStatus', max_length=16, null=True)  # Field name made lowercase.
    ticketpriority = models.CharField(db_column='TicketPriority', max_length=6, blank=True, null=True)  # Field name made lowercase.
    ticketdescription = models.TextField(db_column='TicketDescription', blank=True, null=True)  # Field name made lowercase.
    ticketsubject = models.CharField(db_column='TicketSubject', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ticketcreatedby = models.CharField(db_column='TicketCreatedBy', max_length=255, blank=True, null=True)  # Field name made lowercase.
    ticketcategorytransid = models.ForeignKey(QitTicketcategory, models.DO_NOTHING, db_column='TicketCategoryTransId', blank=True, null=True)  # Field name made lowercase.
    ticketsubcattransid = models.ForeignKey(QitTicketsubcategory, models.DO_NOTHING, db_column='TicketSubCatTransId', blank=True, null=True)  # Field name made lowercase.
    companytransid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='CompanyTransId', blank=True, null=True)  # Field name made lowercase.
    customertransid = models.ForeignKey(QitCompanycustomer, models.DO_NOTHING, db_column='CustomerTransId', blank=True, null=True)  # Field name made lowercase.
    usertransid = models.ForeignKey(QitCompanyuser, models.DO_NOTHING, db_column='UserTransId', blank=True, null=True)  # Field name made lowercase.
    ticketdatetime = models.DateTimeField(db_column='TicketDateTime')  # Field name made lowercase.
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)
    ticketattachedfile = models.TextField(db_column='TicketAttachedFile', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'QIT_Tickets'

    def generate_ticketcode(self):
        """Generate a unique ticket code based on the current year and a sequence number."""
        year = datetime.now().year
        prefix = 'TIC'

        # Use the transaction block to ensure atomicity
        with transaction.atomic():
            # Get the last ticket code starting with the prefix and year
            last_ticket = QitTickets.objects.filter(ticketcode__startswith=f"{prefix}{year}").order_by('-ticketcode').first()
            
            suffix = 1
            if last_ticket:
                # Extract the last 4 digits from the ticket code and increment
                last_suffix = int(last_ticket.ticketcode[-4:])
                suffix = last_suffix + 1

            # Generate random letter(s) between A-Z
            letters = ''.join(random.choices(string.ascii_uppercase, k=1))
            ticketcode = f"{prefix}{year}{letters}{suffix:04d}"  # Format ticket code with year, letters, and sequence

            # Ensure the ticket code is unique
            while QitTickets.objects.filter(ticketcode=ticketcode).exists():
                suffix += 1  # Increment the suffix until the ticket code is unique
                ticketcode = f"{prefix}{year}{letters}{suffix:04d}"

            return ticketcode

    def save(self, *args, **kwargs):
        """Override save method to auto-generate ticket code before saving."""
        if not self.ticketcode:
            self.ticketcode = self.generate_ticketcode()  # Generate ticket code before saving
        super(QitTickets, self).save(*args, **kwargs)



class QitUserlogin(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.    
    email = models.CharField(db_column='Email', max_length=255)  # Field name made lowercase.
    password = models.CharField(db_column='Password', max_length=255)  # Field name made lowercase.    
    isotpverified = models.CharField(db_column='IsOtpVerified', max_length=10, blank=True, null=True)  # Field name made lowercase.
    userrole = models.CharField(db_column='UserRole', max_length=255)  # Field name made lowercase.    
    isuserdeleted = models.CharField(db_column='IsUserDeleted', max_length=10, blank=True, null=True)  # Field name made lowercase.
    username = models.CharField(max_length=255, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.IntegerField(blank=True, null=True)
    is_staff = models.IntegerField(blank=True, null=True)
    is_superuser = models.IntegerField(blank=True, null=True)
    entry_date = models.DateTimeField(blank=True, null=True,auto_now_add=True)
    update_date = models.DateTimeField(blank=True, null=True,auto_now=True)

    class Meta:
        managed = False
        db_table = 'QIT_UserLogin'


class QitNotifications(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=255)  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.
    notificationtype = models.CharField(db_column='NotificationType', max_length=50)  # Field name made lowercase.
    notificationstatus = models.CharField(db_column='NotificationStatus', max_length=100, blank=True, null=True)  # Field name made lowercase.
    usertransid = models.ForeignKey(QitCompanyuser, models.DO_NOTHING, db_column='UserTransId', blank=True, null=True)  # Field name made lowercase.
    customertransid = models.ForeignKey(QitCompanycustomer, models.DO_NOTHING, db_column='CustomerTransId', blank=True, null=True)  # Field name made lowercase.
    companytransid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='CompanyTransId', blank=True, null=True)  # Field name made lowercase.
    activitytransid = models.ForeignKey(QitActivities, models.DO_NOTHING, db_column='ActivityTransId', blank=True, null=True)  # Field name made lowercase.
    tickettransid = models.ForeignKey(QitTickets, models.DO_NOTHING, db_column='TicketTransId', blank=True, null=True)  # Field name made lowercase.
    createdby = models.CharField(db_column='CreatedBy', max_length=255, blank=True, null=True)  # Field name made lowercase.
    entrydate = models.DateTimeField(db_column='EntryDate', blank=True, null=True)  # Field name made lowercase.
    updatedate = models.DateTimeField(db_column='UpdateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Qit_Notifications'


# ///// rajvi changes
class QitApilog(models.Model):
    transid = models.AutoField(db_column='TransId', primary_key=True)  # Field name made lowercase.
    module = models.CharField(db_column='Module', max_length=200, blank=True, null=True)  # Field name made lowercase.
    viewname = models.CharField(db_column='ViewName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    methodname = models.CharField(db_column='MethodName', max_length=200, blank=True, null=True)  # Field name made lowercase.
    loglevel = models.CharField(db_column='LogLevel', max_length=2, blank=True, null=True)  # Field name made lowercase.
    logmessage = models.TextField(db_column='LogMessage', blank=True, null=True)  # Field name made lowercase.
    jsonpayload = models.TextField(db_column='JsonPayload', blank=True, null=True)  # Field name made lowercase.
    loginuser = models.CharField(db_column='LoginUser', max_length=80, blank=True, null=True)  # Field name made lowercase.
    userrole = models.CharField(db_column='UserRole', max_length=20, blank=True, null=True)  # Field name made lowercase.
    entrydate = models.DateTimeField(db_column='EntryDate')  # Field name made lowercase.
    cmptransid = models.IntegerField(db_column='CmpTransId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'QIT_ApiLog'

class QitConfiguration(models.Model):
    transid = models.AutoField(primary_key=True)
    company_transid = models.ForeignKey(QitCompany, models.DO_NOTHING, db_column='company_transid')
    primary_email = models.CharField(max_length=255)
    alt_email = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'QIT_Configuration'


class QitCatsubcatmapping(models.Model):
    company = models.ForeignKey(QitCompany, models.DO_NOTHING, blank=True, null=True)
    customer = models.ForeignKey(QitCompanycustomer, models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(QitTicketcategory, models.DO_NOTHING, blank=True, null=True)
    subcategory = models.ForeignKey(QitTicketsubcategory, models.DO_NOTHING, blank=True, null=True)
    entry_date = models.DateTimeField(blank=True, null=True)
    update_date = models.DateTimeField(blank=True, null=True)
    selected = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Qit_CatSubcatMapping'
        unique_together = (('company', 'customer', 'category', 'subcategory'),)