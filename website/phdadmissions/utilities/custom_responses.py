import json

from django.http import HttpResponseBadRequest


def throw_bad_request(error_message):
    response_data = json.dumps({"error": error_message})

    return HttpResponseBadRequest(response_data, content_type='application/json')