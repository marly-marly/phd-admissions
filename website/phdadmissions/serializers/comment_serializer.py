from rest_framework import serializers

from authentication.serializers import AccountSerializer
from phdadmissions.models.comment import Comment


class CommentSerializer(serializers.ModelSerializer):
    supervisor = AccountSerializer

    class Meta:
        model = Comment
        fields = (
        'id', 'content', 'created_at', 'modified_at')
