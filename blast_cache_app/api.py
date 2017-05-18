from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Cache_entry
from .serializers import CacheEntrySerializer


class EntryList(APIView):
    """
        List all cache entries
    """
    def get(self, request, format=None):
        entries = Cache_entry.objects.all()
        serializer = CacheEntrySerializer(entries, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CacheEntrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        entry = self.get_object(md5)
        serializer = CacheEntrySerializer(entry)
        return Response(serializer.data)

    def put(self, request, md5, format=None):
        entry = self.get_object(md5)
        serializer = CacheEntrySerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, md5, format=None):
        entry = self.get_object(md5)
        entry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# from datetime import date
# from dateutil.relativedelta import relativedelta
#
# from django.db.models import Prefetch
# from django.utils import timezone
# from django.http import Http404
# from django.utils.datastructures import MultiValueDictKeyError
# from django.conf import settings
#
# from rest_framework import viewsets
# from rest_framework import mixins
# from rest_framework import generics
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework import request
#
# from .serializers import *
#
# from .models import Cache_entry
#
#
# class CacheDetails(mixins.RetrieveModelMixin,
#                    mixins.CreateModelMixin,
#                    mixins.UpdateModelMixin,
#                    generics.GenericAPIView,
#                    ):
#     """
#         API for gettting or updating cached blast data
#     """
#     lookup_field = 'md5'
#     queryset = Cache_entry.objects.all()
#
#     def get_serializer_class(self):
#         if self.request.method == 'GET':
#             return CacheEntrySerializer
#         if self.request.method == 'POST':
#             return CacheEntrySerializer
#
#     def get(self, request, format=None, *args, **kwargs):
#         """
#             Returns the data files, given an md5
#         """
#         return self.retrieve(request, *args, **kwargs)

    # def put(self, request, *args, **kwargs):
    #     """
    #         Update a PSI-BLAST result
    #     """
    #     request_contents = request.data
    #     try:
    #         data, request_contents = self.__prepare_data(request)
    #     except MultiValueDictKeyError:
    #         content = {'error': "Input does not contain all required fields"}
    #         return Response(content, status=status.HTTP_400_BAD_REQUEST)
    #     except KeyError:
    #         content = {'error': "Input does not contain all required fields"}
    #         return Response(content, status=status.HTTP_400_BAD_REQUEST)
    #
    #     ce = Cache_entry.objects.filter(md5=data['md5'])
    #     if len(ce) == 0:
    #         return Response("Sequence not present",
    #                         status=status.HTTP_400_BAD_REQUEST)
    #
    #     self.__insert_new_files(request, data, ce[0])
    #     return Response("Your files updated", status=status.HTTP_200_OK)
    #
    # def post(self, request, *args, **kwargs):
    #     """
    #         Add a new uniprot ID and then add the pssm/chk
    #     """
    #     # we get the files
    #     # append them to the new file getting the coords
    #     request_contents = request.data
    #     try:
    #         data, request_contents = self.__prepare_data(request)
    #     except MultiValueDictKeyError:
    #         content = {'error': "Input does not contain all required fields"}
    #         return Response(content, status=status.HTTP_400_BAD_REQUEST)
    #     except KeyError:
    #         content = {'error': "Input does not contain all required fields"}
    #         return Response(content, status=status.HTTP_400_BAD_REQUEST)
    #
    #     # check we don't have this particular seq
    #     ce = Cache_entry.objects.filter(md5=data['md5'])
    #     if len(ce) > 0:
    #         return Response("Hey Yo", status=status.HTTP_400_BAD_REQUEST)
    #
    #     ce = Cache_entry.objects.create(uniprotID=data['uniprotID'])
    #     ce.md5 = data['md5']
    #     ce.save()
    #     self.__insert_new_files(request, data, ce)
    #     return Response("Your files were added",
    #                     status=status.HTTP_201_CREATED)
