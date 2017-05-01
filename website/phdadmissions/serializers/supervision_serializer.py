from rest_framework import serializers

from authentication.serializers import AccountSerializer
from phdadmissions.models.supervision import Supervision
from phdadmissions.serializers.comment_serializer import CommentSerializer


class SupervisionSerializer(serializers.ModelSerializer):
    supervisor = AccountSerializer
    comments = CommentSerializer(many=True)

    class Meta:
        model = Supervision
        fields = (
            'id', 'application', 'supervisor', 'acceptance_condition', 'recommendation', 'created_at', 'modified_at',
            "comments")