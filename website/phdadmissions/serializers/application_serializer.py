from rest_framework import serializers, fields

from phdadmissions.models.application import Application, POSSIBLE_FUNDING_CHOICES
from phdadmissions.serializers.academic_year_serializer import AcademicYearSerializer
from phdadmissions.serializers.supervision_serializer import SupervisionSerializer


class ApplicationSerializer(serializers.ModelSerializer):
    supervisions = SupervisionSerializer(many=True, required=False)
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.IntegerField()

    possible_funding = fields.MultipleChoiceField(choices=POSSIBLE_FUNDING_CHOICES)

    class Meta:
        model = Application
        fields = (
            'id', 'registry_ref', 'surname', 'forename', 'possible_funding', 'funding_status', 'origin', 'student_type',
            'status', 'gender', 'research_subject', 'registry_comment', 'created_at', 'modified_at', 'supervisions',
            'academic_year', 'academic_year_id')

    def create(self, validated_data):
        return Application.objects.create(registry_ref=validated_data['registry_ref'],
                                          surname=validated_data['surname'],
                                          forename=validated_data['forename'],
                                          possible_funding=validated_data['possible_funding'],
                                          funding_status=validated_data['funding_status'],
                                          origin=validated_data['origin'],
                                          student_type=validated_data['student_type'],
                                          gender=validated_data['gender'],
                                          research_subject=validated_data['research_subject'],
                                          registry_comment=validated_data['registry_comment'],
                                          academic_year_id=validated_data['academic_year_id'])

    def update(self, application, validated_data):
        application.registry_ref = validated_data['registry_ref']
        application.surname = validated_data['surname']
        application.forename = validated_data['forename']
        application.possible_funding = validated_data['possible_funding']
        application.funding_status = validated_data['funding_status']
        application.origin = validated_data['origin']
        application.student_type = validated_data['student_type']
        application.status = validated_data['status']
        application.gender = validated_data['gender']
        application.research_subject = validated_data['research_subject']
        application.registry_comment = validated_data['registry_comment']
        application.academic_year_id = validated_data['academic_year_id']

        application.save()

        return application
