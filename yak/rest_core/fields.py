from rest_framework.fields import get_attribute
from rest_framework import relations
from rest_framework.reverse import reverse


class GenericHyperlinkedRelatedField(relations.PrimaryKeyRelatedField):
    def get_attribute(self, instance):
        return get_attribute(instance, self.source_attrs)

    def to_representation(self, value):
        default_view_name = "{}s-detail".format(value._meta.object_name.lower())
        url = reverse(default_view_name, kwargs={'pk': value.pk})
        request = self.context.get('request', None)
        if request is not None:
            return request.build_absolute_uri(url)
        return url
