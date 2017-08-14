from rest_framework_jwt.settings import api_settings
import jwt
from rest_framework_jwt.authentication import jwt_get_username_from_payload


# Returns the fields of a particular model
def get_model_fields(model):
    return [f.name for f in model._meta.get_fields()]


# Verifies if a JWT token is valid
def verify_authentication_token(token):
    jwt_decode_handler = api_settings.JWT_DECODE_HANDLER

    try:
        payload = jwt_decode_handler(token)
    except jwt.ExpiredSignature:
        return False, "Signature has expired."
    except jwt.DecodeError:
        return False, "Error decoding signature."

    username = jwt_get_username_from_payload(payload)

    if not username:
        return False, "Invalid payload."

    if not id:
        return False, "Documentation ID was not provided as a GET parameter."

    return True, ''
