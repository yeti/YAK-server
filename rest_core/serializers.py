from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers

__author__ = 'baylee'


class BaseModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(BaseModelSerializer, self).__init__(*args, **kwargs)
        self.fields['content_type'] = serializers.SerializerMethodField('get_content_type')

    def get_content_type(self, obj):
        return ContentType.objects.get_for_model(obj).pk
