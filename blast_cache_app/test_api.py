import hashlib
import os
import json
import random
import datetime

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
    md5 = None

    def setUp(self):
        test_seq = random_string(length=240)
        m = hashlib.md5()
        test_hash = m.update(test_seq.encode('utf-8'))
        self.md5 = m.hexdigest()
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
        response = self.client.get(reverse('entryDetail',
                                           args=[self.ce.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertIn("-num_iterations", response.content.decode("utf-8"))

    def test_post_record(self):
        url = reverse('entryList')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME FILE DATA YO"}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cache_entry.objects.count(), 2)
        # self.assertEqual(Cache_entry.objects.get().name, 'DabApps')

    def test_load_initialises_count_to_zero(self):
        url = reverse('entryList')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME FILE DATA YO"}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(
                        Cache_entry.objects.get(name="test").accessed_count, 0)

    def test_expiry_date_set_correctly(self):
        url = reverse('entryList')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME FILE DATA YO"}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(
                        Cache_entry.objects.get(
                         name="test").expiry_date, datetime.date.today() +
                        datetime.timedelta(days=settings.CACHE_EXPIRY_PERIOD))

    def test_reject_data_if_malformatted(self):
        url = reverse('entryList')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": 0
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.content.decode("utf-8"),
                         "{\"data\":[\"Expected a dictionary of items but got"
                         " type \\\"int\\\".\"]}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_data_with_no_file_data_key(self):
        url = reverse('entryList')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"--num_iterations": 20}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.content.decode("utf-8"),
                         "{\"data\":[\"file_data must be present in data "
                         "field\"]}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_data_with_no_file_data(self):
        url = reverse('entryList')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": ""}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.content.decode("utf-8"),
                         "{\"data\":[\"You have passsed file_data with no "
                         "data\"]}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_with_no_data_for_custom_key(self):
        url = reverse('entryList')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME DATA YO", "--num_iterations": ""}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.content.decode("utf-8"),
                         "{\"data\":[\"You have passsed --num_iterations with"
                         " no data\"]}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
