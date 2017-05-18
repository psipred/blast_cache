import datetime
import json

from django.conf import settings

from rest_framework import serializers
from rest_framework_hstore.fields import HStoreField

from .models import Cache_entry


class CacheEntrySerializer(serializers.ModelSerializer):
    class Meta:
        validators = []
        model = Cache_entry
        fields = ('pk', 'name', 'md5', 'accessed_count', 'created',
                  'modified', 'expiry_date', 'file_type', 'blast_hit_count',
                  'runtime', 'data',)
        read_only_fields = ('accessed_count', 'created', 'modified',
                            'expiry_date',)

    def validate_data(self, value):
        try:
            obj = json.loads(value)
        except:
            raise serializers.ValidationError("Data field does not look like"
                                              "python dict/json")
        if "file_data" not in obj:
            raise serializers.ValidationError("file_data must be present in "
                                              "data field")
        for key, value in obj.items():
            is len(value) == 0:
                raise serializers.ValidationError("You have passsed "+key +
                                                  " with no data")

    def create(self, validated_data):
        entry = Cache_entry(
                name=validated_data['name'],
                md5=validated_data['md5'],
                accessed_count=0,
                expiry_date=datetime.date.today +
                timedelta(days=settings.CACHE_EXPIRY_PERIOD),
                file_type=validated_data['file_type'],
                blast_hit_count=validated_data['blast_hit_count'],
                runtime=validated_data['runtime'],
                data=json.loads(validated_data['data'])
        )
        entry.save()
        return entry
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
