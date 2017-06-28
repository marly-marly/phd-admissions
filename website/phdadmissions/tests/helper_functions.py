import json

from django.contrib.auth.models import User

from assets.constants import *
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


# Prepares a json string that can be used to create / update an application
def create_application_details(academic_year_id, registry_ref="012983234", surname="Szeles",
                               forename="Marton",
                               possible_funding=None, funding_status=PENDING, origin=EU,
                               student_type=COMPUTING, status=PENDING_STATUS, supervisors=None,
                               research_subject="Investigating travelling at the speed of light.",
                               administrator_comment=None, phd_admission_tutor_comment=None, file_descriptions=None, gender=FEMALE, tags=None):

    if possible_funding is None:
        possible_funding = [SELF]
    if file_descriptions is None:
        file_descriptions = []
    if supervisors is None:
        supervisors = ["Atrus1", "Atrus2"]
    if tags is None:
        tags = ["This is a tag", "AnotherTag"]

    return json.dumps({"registry_ref": registry_ref,
                       "surname": surname,
                       "forename": forename,
                       "possible_funding": possible_funding,
                       "funding_status": funding_status,
                       "origin": origin,
                       "student_type": student_type,
                       "status": status,
                       "supervisors": supervisors,
                       "research_subject": research_subject,
                       "administrator_comment": administrator_comment,
                       "phd_admission_tutor_comment": phd_admission_tutor_comment,
                       "file_descriptions": file_descriptions,
                       "academic_year_id": academic_year_id,
                       "gender": gender,
                       "tag_words": tags})


# Sends an HTTP request to create a new application.
def create_new_application(token, post_data, client):

    return client.post(path="/api/applications/application/",
                            data=json.dumps({"application": post_data}),
                            HTTP_AUTHORIZATION='JWT {}'.format(token),
                            content_type='application/json')