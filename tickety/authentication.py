from django.contrib.auth.backends import BaseBackend
from .models import QitUserlogin
from django.contrib.auth.hashers import check_password

class EmailAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = QitUserlogin.objects.get(email=email)
            # Debug log to ensure the password comparison logic is correct
            print(f"Provided password: {password}, Stored password: {user.password}")
            if check_password(password, user.password):
                return user
            else:
                print("Password mismatch.")
        except QitUserlogin.DoesNotExist:
            print(f"User with email {email} does not exist.")
            return None
