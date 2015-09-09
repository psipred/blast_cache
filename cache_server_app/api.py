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
        if len(ce)==0:
            raise Http404

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
            Returns the chk and pssm files, given an md5
        """
        return self.retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
            Update a PSI-BLAST result
        """
        return self.retrieve(request, *args, **kwargs)

    def __prepare_data(self, request):
        request_contents = request.data
        data = {}
        try:
            data['md5'] = request_contents.pop('md5')[0]
            data['hit_count'] = request_contents.pop('hit_count')[0]
            data['uniprotID'] = request_contents.pop('uniprotID')[0]
        except MultiValueDictKeyError:
            raise MultiValueDictKeyError
        except KeyError:
            raise KeyError

        return(data, request_contents)

    def __pseudo_lock_write(self, write_file, lock_file, string):
        if os.path.isfile(write_file):
            while os.path.isfile(lock_file):
                time.sleep(5)
            open(lock_file, 'a').close()
            f = open(write_file, 'a')
            f.write(string)
            f.flush()
            f.close()
            os.remove(lock_file)

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

        pssm_size = os.path.getsize(settings.USER_PSSM)
        chk_size = os.path.getsize(settings.USER_CHK)
        self.__pseudo_lock_write(settings.USER_CHK, settings.CHK_LOCK, "testing")
        self.__pseudo_lock_write(settings.USER_PSSM, settings.PSSM_LOCK, "testing")

        return Response("Hey Yo", status=status.HTTP_201_CREATED)


class UploadFile(mixins.CreateModelMixin,
                 generics.GenericAPIView,):

    def get_file_coordinates(self, file, start_re, stop_re):
        result_dict = {}
        with open(file, "rb") as pssmfile:
            uniprotID = ""
            start = 0
            stop = 0
            for byteline in pssmfile:
                line = byteline.decode("utf-8")
                match = re.match(start_re, line)
                if match:
                    uniprotID = match.group(1)
                    start = pssmfile.tell()

                match = re.match(stop_re, line)
                if match:
                    stop = pssmfile.tell()-len(line)
                    result_dict[uniprotID] = [start, stop]
        return(result_dict)

    def insert_file_details(self, ce, file_location, file_type,
                            start, stop, hits):
        exp_date = date.today() + relativedelta(months=+6)
        f = File.objects.create(cache_entry=ce, expiry_date=exp_date)
        f.accessed_count = 0
        f.file_location = file_location
        f.file_type = file_type
        f.file_byte_start = start
        f.file_byte_stop = stop
        f.blast_hits = hits
        f.save()

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

        if not os.path.isfile(pssm_file) or not os.path.isfile(chk_file) \
           or not os.path.isfile(fasta_file):
            content = {'error': "One or more of your files does not exist"}
            return Response(content, status=status.HTTP_400_BAD_REQUEST)

        # get a dict of all the chk & pssm boundaries
        pssm_dict = self.get_file_coordinates(pssm_file,
                                              ">>>START FILE: (.+)\.pssm",
                                              ">>>STOP FILE: (.+)\.pssm")
        chk_dict = self.get_file_coordinates(chk_file,
                                             ">>>START FILE: (.+)\.chk",
                                             ">>>STOP FILE: (.+)\.chk")
        # pp = pprint.PrettyPrinter(indent=2)
        # pp.pprint(pssm_dict)
        # pp.pprint(chk_dict)
        id_re = re.compile(">.{2}\|(.+?)\|.+?\s")
        with open(fasta_file, "rb") as fastafile:
            for byteline in fastafile:
                line = byteline.decode("utf-8")
                m = hashlib.md5()
                if line.startswith(">"):
                    match = re.match(id_re, line)
                    uniprotID = match.group(1)
                    byteseq = next(fastafile)
                    seq = byteseq.decode("utf-8")
                    seq = seq.strip()
                    m.update(seq.encode('utf-8'))
                    md5 = m.hexdigest()
                    print("Inserting Details for: "+uniprotID)
                    ce = Cache_entry.objects.create(uniprotID=uniprotID)
                    ce.md5 = md5
                    ce.save()
                    self.insert_file_details(ce,
                                             pssm_file,
                                             File.PSSM,
                                             pssm_dict[uniprotID][0],
                                             pssm_dict[uniprotID][1],
                                             0)
                    self.insert_file_details(ce,
                                             chk_file,
                                             File.CHK,
                                             chk_dict[uniprotID][0],
                                             chk_dict[uniprotID][1],
                                             0)
        content = {"Fasta file, pssm and chk data uploaded"}
        return Response(content, status=status.HTTP_201_CREATED)
