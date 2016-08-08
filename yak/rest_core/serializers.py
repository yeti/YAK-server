from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class YAKModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        super(YAKModelSerializer, self).__init__(*args, **kwargs)
        self.fields['content_type'] = serializers.SerializerMethodField()

    def get_content_type(self, obj):
        return ContentType.objects.get_for_model(obj).pk
