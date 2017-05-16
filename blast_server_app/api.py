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

    def __prepare_data(self, request):
        request_contents = request.data
        data = {}
        try:
            data['md5'] = request_contents.pop('md5')[0]
            data['hit_count'] = request_contents.pop('hit_count')[0]
            data['uniprotID'] = request_contents.pop('uniprotID')[0]
            data['runtime'] = request_contents.pop('runtime')[0]
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

    def __insert_new_files(self, request, data, ce):
        pssm_size = os.path.getsize(settings.USER_PSSM)+1
        chk_size = os.path.getsize(settings.USER_CHK)+1
        pssm_data = request.FILES['pssm_file'].read().decode("utf-8")
        chk_data = request.FILES['chk_file'].read().decode("utf-8")
        pssm_string = ">>>START FILE: "+data['uniprotID']+".pssm\n"
        pssm_string += pssm_data+"\n"
        pssm_string += ">>>STOP FILE: "+data['uniprotID']+".pssm\n"
        chk_string = ">>>START FILE: "+data['uniprotID']+".chk\n"
        chk_string += chk_data+"\n"
        chk_string += ">>>STOP FILE: "+data['uniprotID']+".chk\n"

        self.__pseudo_lock_write(settings.USER_CHK,
                                 settings.CHK_LOCK, chk_string)
        self.__pseudo_lock_write(settings.USER_PSSM,
                                 settings.PSSM_LOCK, pssm_string)
        pssm_start = pssm_size+20+len(data['uniprotID'])
        pssm_stop = pssm_start+len(pssm_data)
        chk_start = chk_size+19+len(data['uniprotID'])
        chk_stop = chk_start+len(chk_data)

        File.insert_file_details(ce=ce,
                                 file_location=settings.USER_PSSM,
                                 file_type=File.PSSM,
                                 start=pssm_start,
                                 stop=pssm_stop,
                                 hits=data['hit_count'],
                                 runtime=data['runtime'])
        File.insert_file_details(ce=ce,
                                 file_location=settings.USER_CHK,
                                 file_type=File.CHK,
                                 start=chk_start,
                                 stop=chk_stop,
                                 hits=data['hit_count'],
                                 runtime=data['runtime'])

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        md5 = self.kwargs['md5']
        # TODO: Three queries here, should be able to make this two or fewer!
        ce = Cache_entry.objects.filter(md5=md5)
        if len(ce) == 0:
            raise Http404

        f_pssm = None
        f_chk = None
        f = None
        try:
            f_pssm = File.objects.filter(cache_entry=ce,
                                         file_type=File.PSSM).latest()
            f_pssm.accessed_count += 1
            f_pssm.save()
        except:
            # Should warn that the record has no PSSM
            pass
        try:
            f_chk = File.objects.filter(cache_entry=ce,
                                        file_type=File.CHK).latest()
            f_chk.accessed_count += 1
            f_chk.save()
        except:
            # Should warn that the record has no CHK
            pass

        if f_pssm is not None:
            f = f_pssm
        elif f_chk is not None:
            f = f_chk

        if f_pssm is not None and f_chk is not None:
            if f_pssm.created > f_chk.created:
                f = f_chk

        queryset = Cache_entry.objects.filter(md5=md5).prefetch_related(
                   Prefetch("file_set", queryset=File.objects.filter(
                            created__gte=f.created)))
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
                    File.insert_file_details(ce=ce,
                                             file_location=pssm_file,
                                             file_type=File.PSSM,
                                             start=pssm_dict[uniprotID][0],
                                             stop=pssm_dict[uniprotID][1],
                                             hits=0,
                                             runtime=None)
                    File.insert_file_details(ce=ce,
                                             file_location=chk_file,
                                             file_type=File.CHK,
                                             start=chk_dict[uniprotID][0],
                                             stop=chk_dict[uniprotID][1],
                                             hits=0,
                                             runtime=None)
        content = {"Fasta file, pssm and chk data uploaded"}
        return Response(content, status=status.HTTP_201_CREATED)
