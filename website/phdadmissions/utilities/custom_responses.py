import json

from django.http import HttpResponseBadRequest
from django.utils.translation import ugettext


def throw_bad_request(error_message):
    response_data = json.dumps({"error": error_message})

    return HttpResponseBadRequest(response_data, content_type='application/json')


def throw_invalid_data(errors):
    error_message = ""
    for key in errors:
        field_errors = [ugettext(error) for error in errors[key]]
        field_error_message = " ".join(field_errors)
        error_message += "{}: {} <br>".format(key, field_error_message)

    return throw_bad_request(error_message)