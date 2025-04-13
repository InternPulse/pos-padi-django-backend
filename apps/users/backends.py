# apps/users/backends.py
from django.contrib.auth.backends import ModelBackend
from .models import User

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Support email as username parameter
        email = kwargs.get("email", username)
        print(f"Attempting to authenticate user with email: {email}")  # Debugging log
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            print(f"User with email {email} does not exist.")  # Debugging log
            return None

        if user.check_password(password):
            print(f"Authentication successful for user: {email}")  # Debugging log
            return user
        print(f"Password mismatch for user: {email}")  # Debugging log
        return None
