import datetime
import json
import copy
import hashlib

from django.http import Http404
from django.http import QueryDict
from django.db import transaction
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Cache_entry
from .serializers import CacheEntrySerializer


class FullList(APIView):
    """
        list everything in the cache
    """
    def get(self, request, format=None):
        entries = Cache_entry.objects.all()
        # should remove entries where today's date is > expiry date
        serializer = CacheEntrySerializer(entries, many=True)
        return Response(serializer.data)


class EntryList(APIView):
    """
        List all cache entries with a given md5
    """
    # change to only list things with same md5
    def get(self, request, md5, format=None):
        entries = Cache_entry.objects.all().filter(
                  md5=md5,
                  expiry_date__gte=datetime.date.today(),)
        if len(entries) == 0:
            return Response("No Records Available",
                            status=status.HTTP_404_NOT_FOUND)
        # should remove entries where today's date is > expiry date
        serializer = CacheEntrySerializer(entries, many=True)
        return Response(serializer.data)


class EntryDetail(APIView):
    """
    Retrieve, update or delete a snippet instance.
    """
    def get_object(self, md5):
        try:
            return Cache_entry.objects.get(md5=md5)
        except Cache_entry.DoesNotExist:
            raise Http404

    @transaction.atomic()
    def get(self, request, md5, format=None):
        # print(Cache_entry.objects.all())
        block = False
        request_copy = copy.deepcopy(request.GET)
        request_copy.pop('block', None)
        request_copy.pop('file_data', None)
        if request.GET.get('block'):
            if 'true' in request.GET.get('block'):
                block = True
        hstore_key_list = ["file_data", ]
        key_size = len(request_copy)
        # print("KEY SIZE", key_size)
        all_entries = Cache_entry.objects.all()
        # print(request_copy)
        try:
            entries = Cache_entry.objects.all().filter(md5=md5)\
                    .filter(expiry_date__gte=datetime.date.today())\
                    .filter(data__contains=request_copy)
        except Exception as e:
            # print(str(e))
            if block:
                ce = Cache_entry.objects.create(md5=md5,
                                                expiry_date=datetime.date.today() +
                                                datetime.timedelta(days=settings.CACHE_EXPIRY_PERIOD),
                                                data=request_copy,
                                                blocked=True)
                return Response("No Objects Found. Holding Record Created",
                                status=status.HTTP_201_CREATED)
            return Response("No Objects Available",
                            status=status.HTTP_404_NOT_FOUND)
        all = Cache_entry.objects.all()
        # print(entries[0].data)
        if len(entries) == 0:
            if block:
                ce = Cache_entry.objects.create(md5=md5,
                                                expiry_date=datetime.date.today() +
                                                datetime.timedelta(days=settings.CACHE_EXPIRY_PERIOD),
                                                data=request_copy,
                                                blocked=True)
                return Response("No Entries Available. Holding Record Created",
                                status=status.HTTP_201_CREATED)
            return Response("No Entries Available",
                            status=status.HTTP_404_NOT_FOUND)
        valid_count = 0
        returning_entry = None
        for entry in entries:
            # print("entry key size", len(entry.data.keys()), entry.data.keys())
            if len(entry.data.keys()) == 0 and len(entry.data.keys()) == key_size:
                returning_entry = entry
                valid_count += 1
            if len(entry.data.keys()) == key_size+1:
                returning_entry = entry
                valid_count += 1

        if valid_count > 1:
            return Response("Can't Unambiguously Resolve Request",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if valid_count == 0:
            if block:
                ce = Cache_entry.objects.create(md5=md5,
                                                expiry_date=datetime.date.today() +
                                                datetime.timedelta(days=settings.CACHE_EXPIRY_PERIOD),
                                                data=request_copy,
                                                blocked=True
                                                )
                return Response("No Valid Record Available. Holding Record Created",
                                status=status.HTTP_201_CREATED)
            return Response("No Valid Record Available",
                            status=status.HTTP_404_NOT_FOUND)
        serializer = CacheEntrySerializer(returning_entry)
        returning_entry.accessed_count += 1
        returning_entry.save()
        return Response(serializer.data)

    @transaction.atomic()
    def post(self, request, format=None):
        data_copy = {}
        data_copy['name'] = request.data['name']
        data_copy['md5'] = request.data['md5']
        data_copy['file_type'] = request.data['file_type']
        data_copy['runtime'] = request.data['runtime']
        data_copy['blast_hit_count'] = request.data['blast_hit_count']
        data_copy['data'] = request.data['data']
        data_copy['sequence'] = request.data['sequence']

        block = True
        # print(request.GET)
        # print(request.data)
        if 'block' in request.data:
            if 'false' in request.data['block']:
                block = False
        if request.GET.get('block'):
            if 'false' in request.GET.get('block'):
                block = False

        if type(data_copy['data']) is not dict and \
           type(data_copy['data']) is str:
            try:
                data_copy['data'] = data_copy['data'].replace("'", '"')
                data_copy['data'] = json.loads(data_copy['data'])
            except Exception as e:
                return Response("Data malformatted: "+str(e),
                                status=status.HTTP_400_BAD_REQUEST)

        serializer = CacheEntrySerializer(data=data_copy)
        if serializer.is_valid():
            entry = None
            search_components = copy.deepcopy(serializer.validated_data['data'])
            # print(search_components)
            search_components.pop('file_data', None)
            search_components.pop('block', None)
            try:
                entry = Cache_entry.objects.get(
                        md5=serializer.validated_data['md5'],
                        expiry_date__gte=datetime.date.today(),
                        data__contains=search_components)
            except Exception as e:
                pass
            # print("BLOCK STATUS", block)
            if entry is not None:
                if not block:
                    entry.name = data_copy['name']
                    entry.md5 = data_copy['md5']
                    entry.file_type = data_copy['file_type']
                    entry.runtime = data_copy['runtime']
                    entry.blast_hit_count = data_copy['blast_hit_count']
                    entry.data = data_copy['data']
                    entry.sequence = data_copy['sequence']
                    entry.blocked = False
                    entry.save()
                    return Response("Record Updated",
                                    status=status.HTTP_200_OK)
                return Response("Valid Record Available",
                                status=status.HTTP_409_CONFLICT)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
