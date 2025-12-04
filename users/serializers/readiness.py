from rest_framework import serializers
from users.models import ReadinessLevel

class ReadinessLevelSerializer(serializers.ModelSerializer):
    """Serializer for ReadinessLevel model"""
    class Meta:
        model = ReadinessLevel
        fields = (
            'id',
            'startup',
            'type',
            'level',
            'title',
            'subtitle',
            'created',
            'updated',
        )
        read_only_fields = ('id', 'startup', 'created', 'updated')
