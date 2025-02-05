from rest_framework.exceptions import ValidationError
from tickety.models import QitCompanycustomer, QitCompanyuser, QitCompany
from functools import wraps

def validate_email_uniqueness(email):
    """
    Check if the given email already exists in any of the three tables.
    Raise a ValidationError if the email is found.
    """
    if QitCompany.objects.filter(cmpemail=email).exists():
        raise ValidationError(f"Email {email} already exists in the company table.")
    if QitCompanycustomer.objects.filter(cmpemail=email).exists():
        raise ValidationError(f"Email {email} already exists in the customer table.")
    if QitCompanyuser.objects.filter(cmpemail=email).exists():
        raise ValidationError(f"Email {email} already exists in the company user table.")
