from rest_framework import serializers

from phdadmissions.models.configuration import Configuration


class ConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Configuration
        fields = ("id", 'name', 'value', 'created_at', 'modified_at')
