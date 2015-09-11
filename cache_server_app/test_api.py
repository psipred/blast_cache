import hashlib
import os
import json

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from .api import *
from .models import *
from .model_factories import *


class CacheEntryTests(APITestCase):

    factory = APIRequestFactory()
    ce = None
    fe = None
    data = {}

    def setUp(self):
        self.ce = CacheEntryFactory.create()
        self.f1 = FileFactory.create(cache_entry=self.ce)

        self.pssm = SimpleUploadedFile('test.pssm',
                                       bytes('SOME PSSM CONTENTS',
                                             'utf-8'))
        self.chk = SimpleUploadedFile('test.chk',
                                      bytes('SOME CHK CONTENTS',
                                            'utf-8'))

        self.inputdata = {'pssm_file': self.pssm,
                          'chk_file': self.chk,
                          'md5': 'a452652e0879d22a04618efb004a03c5',
                          'hit_count': 500,
                          'uniprotID': "P023423",
                          'runtime': 30 }

    def setUpClass():
        open(settings.USER_PSSM, 'a').close()
        open(settings.USER_CHK, 'a').close()

    def tearDownClass():
        # os.remove(settings.USER_PSSM)
        # os.remove(settings.USER_CHK)
        pass

    def tearDown(self):
        Cache_entry.objects.all().delete()
        File.objects.all().delete()

    def test_get_returns_entry(self):
        response = self.client.get(reverse('cacheDetail',
                                           args=[self.ce.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        date = str(self.f1.expiry_date)
        date = date[:10] + 'T' + date[11:]
        date = date[:26] + 'Z'
        test_data = '{{"uniprotID":"{0}","md5":"{1}",'.format(
                                                       self.ce.uniprotID,
                                                       self.ce.md5)
        test_data += '"file_set":[{{"accessed_count":{0},'.format(
                     self.f1.accessed_count)
        test_data += '"expiry_date":"{0}","file_type":{1},'.format(
                     date, self.f1.file_type)
        test_data += '"blast_hits":{0}}}]}}'.format(self.f1.blast_hits)
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_get_returns_latest_files(self):
        # self.maxDiff = None
        f2 = FileFactory.create(cache_entry=self.ce)
        response = self.client.get(reverse('cacheDetail',
                                           args=[self.ce.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        date = str(f2.expiry_date)
        date = date[:10] + 'T' + date[11:]
        date = date[:26] + 'Z'
        test_data = '{{"uniprotID":"{0}","md5":"{1}",'.format(
                                                       self.ce.uniprotID,
                                                       self.ce.md5)
        test_data += '"file_set":[{{"accessed_count":{0},'.format(
                     f2.accessed_count)
        test_data += '"expiry_date":"{0}","file_type":{1},'.format(
                                                            date,
                                                            f2.file_type)
        test_data += '"blast_hits":{0}}}]}}'.format(f2.blast_hits)
        self.assertEqual(response.content.decode("utf-8"), test_data)

    def test_with_proper_data_load_we_get_2_files(self):
        base = settings.BASE_DIR+"/files/"
        request = self.factory.post(reverse('uploadFile'),
                                    {'fasta_file': base+"all.fasta",
                                     'pssm_file': base+"all.pssm",
                                     'chk_file': base+"all.chk", })
        view = UploadFile.as_view()
        response = view(request)
        md5 = "eb8783411250a01a2bfabb6926ffc2cc"
        response = self.client.get(reverse('cacheDetail',
                                           args=[md5, ]) + ".json")
        response.render()
        data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(data['file_set']), 2)
        chk_count = 0
        pssm_count = 0
        for f in data['file_set']:
            if f['file_type'] == 1:
                pssm_count+=1
            if f['file_type'] == 2:
                chk_count+=1
        self.assertEqual(chk_count, 1)
        self.assertEqual(pssm_count, 1)

    # If we upload some real data do we get the correct information back?
    def test_return_a_correct_entry(self):
        base = settings.BASE_DIR+"/files/"
        request = self.factory.post(reverse('uploadFile'),
                                    {'fasta_file': base+"all.fasta",
                                     'pssm_file': base+"all.pssm",
                                     'chk_file': base+"all.chk", })
        view = UploadFile.as_view()
        response = view(request)
        md5 = "a452652e0879d22a04618efb004a03c5"
        response = self.client.get(reverse('cacheDetail',
                                           args=[md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.request = self.factory.get(reverse('cacheDetail')+md5)

    def test_404_on_bad_request(self):
        md5 = "a452652e0879d22a04618efb004a03c3"
        response = self.client.get(reverse('cacheDetail',
                                           args=[md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # self.request = self.factory.get(reverse('cacheDetail')+md5)

    def test_post_a_novel_set_of_files(self):
        request = self.factory.post(reverse('cache'), self.inputdata,
                                    format='multipart')
        view = CacheDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        files = File.objects.all()
        self.assertEqual(len(files), 3)
        seqs = Cache_entry.objects.filter(uniprotID="P023423")
        self.assertEqual(len(seqs), 1)

    def test_reject_a_file_post_if_entry_exists(self):
        request = self.factory.post(reverse('cache'), self.inputdata,
                                    format='multipart')
        view = CacheDetails.as_view()
        response = view(request)
        request = self.factory.post(reverse('cache'), self.inputdata,
                                    format='multipart')
        view = CacheDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_an_existing_entry(self):
        request = self.factory.post(reverse('cache'), self.inputdata,
                                    format='multipart')
        view = CacheDetails.as_view()
        response = view(request)
        request = self.factory.put(reverse('cache'), self.inputdata,
                                   format='multipart')
        view = CacheDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        seqs = Cache_entry.objects.filter(uniprotID="P023423")
        self.assertEqual(len(seqs), 1)
        self.assertEqual(len(seqs[0].file_set.all()), 4)

    def test_reject_update_if_entry_nonexistant(self):
        request = self.factory.put(reverse('cache'), self.inputdata,
                                   format='multipart')
        view = CacheDetails.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_access_counter_incremented_on_each_get(self):
        pass
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UploadFileTests(APITestCase):

    factory = APIRequestFactory()
    request = None
    base = settings.BASE_DIR+"/files/"

    def setUp(self):
        self.request = self.factory.post(reverse('uploadFile'),
                                         {'fasta_file': self.base+"all.fasta",
                                          'pssm_file': self.base+"all.pssm",
                                          'chk_file': self.base+"all.chk", })

    def tearDown(self):
        Cache_entry.objects.all().delete()
        File.objects.all().delete()

    def test_upload_large_file(self):
        view = UploadFile.as_view()
        response = view(self.request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        files = File.objects.all()
        self.assertEqual(len(files), 8)
        seqs = Cache_entry.objects.all()
        self.assertEqual(len(seqs), 4)

    def test_upload_fails_with_missing_file(self):
        request = self.factory.post(reverse('uploadFile'),
                                    {'fasta_file': self.base+"dall.fasta",
                                     'pssm_file': self.base+"all.pssm",
                                     'chk_file': self.base+"all.chk", })
        view = UploadFile.as_view()
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
