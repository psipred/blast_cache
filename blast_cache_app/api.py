import datetime

from django.http import Http404
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

    def get(self, request, md5, format=None):
        hstore_key_list = ["file_data", ]
        try:
            entry = Cache_entry.objects.get(
                    md5=md5,
                    expiry_date__gte=datetime.date.today(),
                    data__contains=request.GET,)
        except Exception as e:
            return Response("No Record Available",
                            status=status.HTTP_404_NOT_FOUND)
        serializer = CacheEntrySerializer(entry)
        entry.accessed_count += 1
        entry.save()
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CacheEntrySerializer(data=request.data)
        if serializer.is_valid():
            entry = None
            search_components = serializer.validated_data['data']
            search_components.pop('file_data', None)
            try:
                entry = Cache_entry.objects.get(
                        md5=serializer.validated_data['md5'],
                        expiry_date__gte=datetime.date.today(),
                        data__contains=search_components)
            except Exception as e:
                pass
            if entry is not None:

                return Response("Valid Record Available",
                                status=status.HTTP_409_CONFLICT)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
