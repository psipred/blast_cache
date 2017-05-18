from rest_framework import serializers
from rest_framework_hstore.fields import HStoreField

from .models import Cache_entry


class CacheEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Cache_entry
        fields = ('pk', 'name', 'md5', 'accessed_count', 'created',
                  'modified', 'expiry_date', 'file_type', 'blast_hit_count',
                  'runtime', 'data')
    # id = serializers.IntegerField(read_only=True, )
    # name = serializers.CharField(required=True, allow_blank=False,
    #                              max_length=128)
    # md5 = serializers.CharField(required=True, allow_blank=False,
    #                             max_length=64)
    # accessed_count = serializers.IntegerField(read_only=True, )
    # expiry_date = serializers.DateField(read_only=True, )
    # file_type = serializers.ChoiceField(choices=Cache_entry.FILE_CHOICES,
    #                                     required=True, allow_blank=False,)
    # blast_hit_count = serializers.IntegerField(required=True, )
    # runtime = serializers.IntegerField(required=True, )
    # data = HStoreField(required=True)
