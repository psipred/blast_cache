import pprint

from django.db.models import Prefetch

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework import request

from .serializers import CacheEntryOutputSerializer, FileOutputSerializer
from .serializers import CacheEntryInputSerializer, FileInputSerializer

from .models import Cache_entry, File
from .forms import CacheEntryForm, FileForm


class CacheDetails(mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        mixins.UpdateModelMixin,
                        generics.GenericAPIView,
                        ):
    """
        API for gettting or updating cached blast data
    """
    lookup_field = 'md5'

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        pp = pprint.PrettyPrinter(indent=2)
        md5 = self.kwargs['md5']
        #TODO: Three queries here, should be able to make this two or fewer!
        ce = Cache_entry.objects.filter(md5=md5)
        f = File.objects.filter(cache_entry=ce).latest()
        queryset = Cache_entry.objects.filter(md5=md5).prefetch_related(Prefetch("file_set", queryset=File.objects.filter(created=f.created) ))
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return CacheEntryOutputSerializer
        if self.request.method == 'POST':
            return CacheEntryInputSerializer

    def get(self, request, format=None, *args, **kwargs):
        """
            Returns the chk and pssm files
        """
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
            Update a PSI-BLAST result
        """
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
            Add a new uniprot ID and then add the pssm/chk
        """
        return self.retrieve(request, *args, **kwargs)
