from rest_framework import serializers

from .models import Cache_entry, File


class FileOutputSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ('accessed_count', 'expiry_date', 'file_type', 'blast_hits',
                  'file_byte_start', 'file_byte_stop')


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


class FileUploadSerializer(serializers.ModelSerializer):
    pssm_file = serializers.CharField()
    chk_file = serializers.CharField()
    fasta_file = serializers.CharField()

    class Meta:
        model = Cache_entry
        fields = ('pssm_file', 'chk_file', 'fasta_file')
