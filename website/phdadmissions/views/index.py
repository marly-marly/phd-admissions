from django.http import HttpResponse
from django.template import loader
from rest_framework import permissions
from rest_framework.views import APIView


class IndexView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        template = loader.get_template('phdadmissions/index.html')

        return HttpResponse(template.render())