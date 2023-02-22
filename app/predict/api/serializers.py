from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from core.models import Predict, UserProfile


class PredictImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Predict
        fields = ['id', 'owner', 'image',]
        read_only_fields = ['id',]
        extra_kwargs = {
            'image': {'required': True},
        }
    
    # def validate(self, data):
    #     pass


class PredictSerializer(serializers.ModelSerializer):
    class Meta:
        model = Predict
        fields = "__all__"