from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import QitCompany, QitCompanyuser, QitCompanycustomer, QitUserlogin


@receiver(post_save, sender=QitCompanycustomer)
def create_customer_user_login(sender, instance, created, **kwargs):
    if created:
        QitUserlogin.objects.create(
            email=instance.custemail,
            password=instance.custpassword,  # Ensure this is hashed before saving
            userrole="customer",
            is_active=instance.custstatus.lower() == "active",
        )


@receiver(post_save, sender=QitCompanyuser)
def create_company_user_login(sender, instance, created, **kwargs):
    if created:
        QitUserlogin.objects.create(
            email=instance.cmpuseremail,
            password=instance.cmpuserpassword,  # Ensure this is hashed before saving
            userrole="companyuser",
            is_active=instance.cmpuserstatus.lower() == "active",
        )


@receiver(post_save, sender=QitCompany)
def create_company_user_login(sender, instance, created, **kwargs):
    if created:
        QitUserlogin.objects.create(
            email=instance.companyemail,
            password=instance.companypassword,  # Ensure this is hashed before saving
            userrole="company",
            is_active=instance.companystatus.lower() == "active",
        )
