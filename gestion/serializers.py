# serializers.py

from rest_framework import serializers
from .models import HistoriqueAction

class HistoriqueActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoriqueAction
        fields = '__all__'
