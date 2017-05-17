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
    base = settings.BASE_DIR+"/files/"

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
                          'runtime': 30}

    def setUpClass():
        open(settings.USER_PSSM, 'a').close()
        open(settings.USER_CHK, 'a').close()

    def tearDownClass():
        os.remove(settings.USER_PSSM)
        os.remove(settings.USER_CHK)

    def tearDown(self):
        Cache_entry.objects.all().delete()

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
                     self.f1.accessed_count+1)
        test_data += '"expiry_date":"{0}","file_type":{1},'.format(
                     date, self.f1.file_type)
        test_data += '"blast_hits":{0},'.format(self.f1.blast_hits)
        test_data += '"file_byte_start":{0},'.format(self.f1.file_byte_start)
        test_data += '"file_byte_stop":{0}}}]}}'.format(self.f1.file_byte_stop)
        self.assertEqual(response.content.decode("utf-8"), test_data)
