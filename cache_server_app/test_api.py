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

    ce = None
    fe = None

    def setUp(self):
        self.ce = CacheEntryFactory.create()
        self.f1 = FileFactory.create(cache_entry=self.ce)

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
        test_data = '{{"uniprotID":"{0}","md5":"{1}",'.format(self.ce.uniprotID,
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
        self.assertEqual(response.status_code, 200)
        date = str(f2.expiry_date)
        date = date[:10] + 'T' + date[11:]
        date = date[:26] + 'Z'
        test_data = '{{"uniprotID":"{0}","md5":"{1}",'.format(self.ce.uniprotID,
                                                              self.ce.md5)
        test_data += '"file_set":[{{"accessed_count":{0},'.format(
                     f2.accessed_count)
        test_data += '"expiry_date":"{0}","file_type":{1},'.format(date,
                                                                   f2.file_type)
        test_data += '"blast_hits":{0}}}]}}'.format(f2.blast_hits)
        self.assertEqual(response.content.decode("utf-8"), test_data)

    # If we upload some real data do we get the correct information back?
    # def test_return_a_correct_pssm_and_chk(self):
    #   base = settings.BASE_DIR+"/files/"
    #   self.request = self.factory.post(reverse('uploadFile'),
    #                         {'fasta_file': base+"all.fasta",
    #                          'pssm_file': base+"all.pssm",
    #                          'chk_file': base+"all.chk", })
    #     view = UploadFile.as_view()
    #     response = view(request)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     # read in a fasta file, take the md5 and then look up
    #     request = self.factory.get(reverse('cacheDetail'))


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
