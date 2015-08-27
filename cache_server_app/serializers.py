from rest_framework import serializers

from .models import Cache_entry, File


class FileOutputSerializer (serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('accessed_count', 'expiry_date', 'file_type', 'blast_hits')


class CacheEntryOutputSerializer (serializers.ModelSerializer):
    results = FileOutputSerializer(many=True)

    class Meta:
        model = Cache_entry
        fields = ('uniprotID', 'md5')


class FileInputSerializer (serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('file_location', 'file_type', 'file_byte_start',
                  'file_byte_stop', 'blast_hits')


class CacheEntryInputSerializer (serializers.ModelSerializer):
    results = FileInputSerializer(many=True)

    class Meta:
        model = Cache_entry
        fields = ('uniprotID', 'md5')
