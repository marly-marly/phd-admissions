from rest_framework import serializers

from phdadmissions.models.academic_year import AcademicYear


class AcademicYearSerializer(serializers.ModelSerializer):

    class Meta:
        model = AcademicYear
        fields = ('id', 'name', 'start_date', 'end_date', 'created_at', 'modified_at')
