from rest_framework import serializers

from authentication.serializers import AccountSerializer
from phdadmissions.models.supervision import Supervision


class SupervisionSerializer(serializers.ModelSerializer):
    supervisor = AccountSerializer

    class Meta:
        model = Supervision
        fields = (
        'id', 'application', 'supervisor', 'acceptance_condition', 'recommendation', 'created_at', 'modified_at')
