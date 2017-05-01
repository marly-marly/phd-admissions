from rest_framework import serializers

from phdadmissions.models.application import Application
from phdadmissions.serializers.supervision_serializer import SupervisionSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    supervisions = SupervisionSerializer(many=True, required=False)

    class Meta:
        model = Application
        fields = (
        'id', 'registry_ref', 'surname', 'forename', 'possible_funding', 'funding_status', 'origin', 'student_type',
        'status', 'research_subject', 'registry_comment', 'created_at', 'modified_at', 'supervisions')

    def create(self, validated_data):
        return Application.objects.create(registry_ref=validated_data['registry_ref'],
                                          surname=validated_data['surname'],
                                          forename=validated_data['forename'],
                                          possible_funding=validated_data['possible_funding'],
                                          funding_status=validated_data['funding_status'],
                                          origin=validated_data['origin'],
                                          student_type=validated_data['student_type'],
                                          status=validated_data['status'],
                                          research_subject=validated_data['research_subject'],
                                          registry_comment=validated_data['registry_comment'])

    def update(self, application, validated_data):
        application.registry_ref = validated_data['registry_ref']
        application.surname = validated_data['surname']
        application.forename = validated_data['forename']
        application.possible_funding = validated_data['possible_funding']
        application.funding_status = validated_data['funding_status']
        application.origin = validated_data['origin']
        application.student_type = validated_data['student_type']
        application.status = validated_data['status']
        application.research_subject = validated_data['research_subject']
        application.registry_comment = validated_data['registry_comment']

        application.save()

        return application
