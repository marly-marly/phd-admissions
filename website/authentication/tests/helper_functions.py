import json

from django.contrib.auth.models import User

from assets.constants import ADMIN
from authentication.models import UserRole


# Creates a new user without using any API endpoint of the website
def create_new_user(username, password, email=None, user_type=ADMIN):
    user = User.objects.create_user(username=username, email=email, password=password)
    UserRole.objects.create(name=user_type, user=user)

    return user


# Logs in a user through the API endpoint, and returns the authentication token for the user
def log_in(client, username, password):
    response = client.post("/api/auth/login/", {"username": username, "password": password})
    response_content = json.loads(response.content.decode('utf-8'))

    return response_content["token"]