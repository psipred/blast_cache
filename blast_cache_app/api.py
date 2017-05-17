import os.path
import hashlib
import re
import pprint
import pytz

from datetime import date
from dateutil.relativedelta import relativedelta

from django.db.models import Prefetch
from django.utils import timezone
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework import request

#from .serializers import CacheEntryOutputSerializer
#from .serializers import CacheEntryInputSerializer

from .models import Cache_entry
from .forms import CacheEntryForm


class CacheDetails(mixins.RetrieveModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   generics.GenericAPIView,
                   ):
    """
        API for gettting or updating cached blast data
    """
    lookup_field = 'md5'


    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CacheEntryOutputSerializer
        if self.request.method == 'POST':
            return CacheEntryInputSerializer

    def get(self, request, format=None, *args, **kwargs):
        """
            Returns the chk and pssm files, given an md5
        """
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        """
            Update a PSI-BLAST result
        """
        request_contents = request.data
        try:
            data, request_contents = self.__prepare_data(request)
        except MultiValueDictKeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        ce = Cache_entry.objects.filter(md5=data['md5'])
        if len(ce) == 0:
            return Response("Sequence not present",
                            status=status.HTTP_400_BAD_REQUEST)

        self.__insert_new_files(request, data, ce[0])
        return Response("Your files updated", status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
            Add a new uniprot ID and then add the pssm/chk
        """
        # we get the files
        # append them to the new file getting the coords
        request_contents = request.data
        try:
            data, request_contents = self.__prepare_data(request)
        except MultiValueDictKeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # check we don't have this particular seq
        ce = Cache_entry.objects.filter(md5=data['md5'])
        if len(ce) > 0:
            return Response("Hey Yo", status=status.HTTP_400_BAD_REQUEST)

        ce = Cache_entry.objects.create(uniprotID=data['uniprotID'])
        ce.md5 = data['md5']
        ce.save()
        self.__insert_new_files(request, data, ce)
        return Response("Your files were added",
                        status=status.HTTP_201_CREATED)
