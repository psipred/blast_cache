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

        self.pssm = SimpleUploadedFile('test.pssm',
                                       bytes('SOME PSSM CONTENTS',
                                             'utf-8'))
        self.chk = SimpleUploadedFile('test.chk',
                                      bytes('SOME CHK CONTENTS',
                                            'utf-8'))

        self.inputdata = {'md5': 'a452652e0879d22a04618efb004a03c5',
                          'hit_count': 500,
                          'uniprotID': "P023423",
                          'runtime': 30}

    # def setUpClass():
    #     open(settings.USER_PSSM, 'a').close()
    #     open(settings.USER_CHK, 'a').close()
    #
    # def tearDownClass():
    #     os.remove(settings.USER_PSSM)
    #     os.remove(settings.USER_CHK)

    def tearDown(self):
        Cache_entry.objects.all().delete()

    def test_get_returns_entry_with_md5(self):
        response = self.client.get(reverse('cacheDetail',
                                           args=[self.ce.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertIn("-num_iterations", response.content.decode("utf-8"))
