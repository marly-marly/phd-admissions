from rest_framework import serializers

from phdadmissions.models.application import Application
from phdadmissions.serializers.supervision_serializer import SupervisionSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    supervisions = SupervisionSerializer(many=True)

    class Meta:
        model = Application
        fields = (
        'id', 'registry_ref', 'surname', 'forename', 'possible_funding', 'funding_status', 'origin', 'student_type',
        'status', 'research_subject', 'registry_comment', 'created_at', 'modified_at', 'supervisions')
