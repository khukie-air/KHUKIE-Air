from rest_framework import serializers
from .models import File, Folder, Trash


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class FileSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = File
        fields = '__all__'


class FolderSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Folder
        fields = '__all__'


class TrashSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = Trash
        fields = '__all__'


'''
[Reference]
Specific fields serializer : https://stackoverflow.com/questions/53319787/how-can-i-select-specific-fields-in-django-rest-framework
'''