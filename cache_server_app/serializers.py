from rest_framework import serializers

from .models import Cache_entry, File


class FileOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('accessed_count', 'expiry_date', 'file_type', 'blast_hits')


class CacheEntryOutputSerializer(serializers.ModelSerializer):
    file_set = FileOutputSerializer(many=True)

    class Meta:
        model = Cache_entry
        fields = ('uniprotID', 'md5', 'file_set')


class FileInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file_location', 'file_type', 'file_byte_start',
                  'file_byte_stop', 'blast_hits')


class CacheEntryInputSerializer(serializers.ModelSerializer):
    file_set = FileInputSerializer(many=True)

    class Meta:
        model = Cache_entry
        fields = ('uniprotID', 'md5', 'file_set')

class CacheEntryUpdateSerializer(serializers.ModelSerializer):
    results = FileInputSerializer(many=True)

    class Meta:
        model = Cache_entry
        fields = ('uniprotID', 'md5')
