import os.path
import hashlib
import re

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
        md5 = self.kwargs['md5']
        # TODO: Three queries here, should be able to make this two or fewer!
        ce = Cache_entry.objects.filter(md5=md5)
        f = File.objects.filter(cache_entry=ce).latest()
        queryset = Cache_entry.objects.filter(md5=md5).prefetch_related(
                   Prefetch("file_set", queryset=File.objects.filter(
                            created=f.created)))
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


class UploadFile(mixins.CreateModelMixin,
                 generics.GenericAPIView,):

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CacheEntryInputSerializer

    def post(self, request, *args, **kwargs):
        """
            We take a 2 file names, find it and then run through it
            adding the details to the db
        """
        pssm_file, chk_file, fasta_file = None, None, None
        try:
            pssm_file = request.data['pssm_file']
            chk_file = request.data['chk_file']
            fasta_file = request.data['fasta_file']
        except Exception as e:
            content = {'error': "Input does not contain all required fields"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        if not os.path.isfile(pssm_file) and not os.path.isfile(chk_file) \
           and not os.path.isfile(fasta_file):
            content = {'error': "One or more of your files does not exist"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        id_re = re.compile(">.{2}\|(.+?)\|.+?\s")
        with open(fasta_file) as fastafile:
            for line in fastafile.readlines():
                m = hashlib.md5()
                if line.startswith(">"):
                    match = re.match(id_re, line)
                    uniprotID = match.group(1)
                    print(fastafile.tell())
                    seq = fastafile.readlines()
                    m.update(seq.encode('utf-8'))
                    md5 = m.hexdigest()


        return self.create(request, *args, **kwargs)
