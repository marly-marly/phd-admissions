from rest_framework import serializers

from authentication.serializers import AccountSerializer
from phdadmissions.models.supervision import Supervision
from phdadmissions.serializers.comment_serializer import CommentSerializer
from phdadmissions.serializers.documentation_serializer import DocumentationSerializer


class SupervisionSerializer(serializers.ModelSerializer):
    supervisor = AccountSerializer()
    comments = CommentSerializer(many=True)
    documentations = DocumentationSerializer(many=True)

    class Meta:
        model = Supervision
        fields = (
            'id', 'supervisor', 'acceptance_condition', 'recommendation', 'created_at', 'modified_at', 'type',
            'creator', 'allocated', 'comments', 'documentations')

    def create(self, validated_data):
        return Supervision.objects.create(acceptance_condition=validated_data['acceptance_condition'],
                                          recommendation=validated_data['recommendation'],
                                          type=validated_data['type'],
                                          creator=validated_data['creator'])

    def update(self, supervision, validated_data):
        if 'acceptance_condition' in validated_data:
            supervision.acceptance_condition = validated_data['acceptance_condition']
        if 'recommendation' in validated_data:
            supervision.recommendation = validated_data['recommendation']

        supervision.save()

        return supervision
