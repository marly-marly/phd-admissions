from rest_framework import serializers

from phdadmissions.models.documentation import Documentation


class DocumentationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Documentation
        fields = ('id', 'file_name', 'file_type', 'description', 'created_at', 'modified_at')
