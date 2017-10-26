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

    def read_pssm(self):
        path = settings.USER_PSSM
        with open(path, 'r') as myfile:
            data = myfile.read()
        return(data)

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

    def test_post_record(self):
        url = reverse('entryDetail')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME FILE DATA YO"}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cache_entry.objects.count(), 2)
        # self.assertEqual(Cache_entry.objects.get().name, 'DabApps')

    def test_load_initialises_count_to_zero(self):
        url = reverse('entryDetail')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME FILE DATA YO"}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(
                        Cache_entry.objects.get(name="test").accessed_count, 0)

    def test_expiry_date_set_correctly(self):
        url = reverse('entryDetail')
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
        url = reverse('entryDetail')
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
        url = reverse('entryDetail')
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
        url = reverse('entryDetail')
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
        url = reverse('entryDetail')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME DATA YO", "--num_iterations": ""}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.content.decode("utf-8"),
                         "{\"data\":[\"You have passsed --num_iterations with"
                         " no data\"]}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_post_with_existing_ids_and_valid_expiry_in_db(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       settings_hash="5f9e6c8f7c71ac9477c3cbc1a6dd8a51",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        url = reverse('entryDetail')
        data = {'name': 'test', 'md5': 'ac1a602a913db2ab48fbf5b1a9e1269a',
                'file_type': 1, 'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME DATA YO",
                         "-num_iterations": "20",
                         "-num_descriptions": "500"}
                }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
#
    def test_accept_post_with_existing_ids_and_expired_in_db(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() -
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       settings_hash="5f9e6c8f7c71ac9477c3cbc1a6dd8a51",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        url = reverse('entryDetail')
        data = {'name': 'test', 'md5': 'ac1a602a913db2ab48fbf5b1a9e1269a',
                'file_type': 1, 'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME DATA YO",
                         "-num_iterations": "20",
                         "-num_descriptions": "500"}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_accept_post_with_existing_ids_and_multiple_expired_in_db(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() -
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       settings_hash="5f9e6c8f7c71ac9477c3cbc1a6dd8a51",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        ce2 = CacheEntryFactory.create(expiry_date=datetime.date.today() -
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD+50),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       settings_hash="5f9e6c8f7c71ac9477c3cbc1a6dd8a51",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})

        url = reverse('entryDetail')
        data = {'name': 'test', 'md5': 'ac1a602a913db2ab48fbf5b1a9e1269a',
                'file_type': 1, 'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME DATA YO",
                         "-num_iterations": "20",
                         "-num_descriptions": "500"}
                }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reject_two_identical_insertions(self):
        url = reverse('entryDetail')
        data = {'name': 'test', 'md5': self.md5, 'file_type': 1,
                'runtime': '80', "blast_hit_count": "500",
                "data": {"file_data": "SOME FILE DATA YO"}
                }
        response = self.client.post(url, data, format='json')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

# GET TESTS BELOW

    def test_get_returns_entry_with_md5(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD))
        response = self.client.get(reverse('entryDetail',
                                           args=[ce1.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertIn("-num_iterations", response.content.decode("utf-8"))

    def test_no_return_for_expired_entries(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() -
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD))
        response = self.client.get(reverse('entryDetail',
                                           args=[ce1.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode("utf-8"),
                         "\"No Record Available\"")

    def test_accessed_count_increments_with_each_request(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       accessed_count=0)
        response = self.client.get(reverse('entryDetail',
                                           args=[ce1.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertIn("\"accessed_count\":1", response.content.decode("utf-8"))
        response = self.client.get(reverse('entryDetail',
                                           args=[ce1.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertIn("\"accessed_count\":2", response.content.decode("utf-8"))

    def test_return_list_with_same_md5(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        ce2 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_cores": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        response = self.client.get(reverse('entryList',
                                           args=[ce1.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json.loads(response.content.decode("utf-8"))), 2)

    def test_return_single_when_list_exists_with_specific_query(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        ce2 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_cores": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        response = self.client.get(reverse('entryDetail',
                                           args=[ce1.md5, ])+".json?"
                                                             "-num_cores=20&"
                                                             "-num_descriptio"
                                                             "ns=500")
        response.render()
        self.assertEqual(response.status_code, 200)

    def test_return_nothing_if_md5_and_custom_key_set_does_not_exist(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        ce2 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_cores": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        response = self.client.get(reverse('entryDetail',
                                           args=[ce1.md5, ])+".json?"
                                                             "-num_alignments"
                                                             "=20&"
                                                             "-num_descriptio"
                                                             "ns=500")
        response.render()
        self.assertEqual(response.status_code, 404)

    def test_return_no_list_if_md5_does_not_exist(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        ce2 = CacheEntryFactory.create(expiry_date=datetime.date.today() +
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_cores": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        response = self.client.get(reverse('entryList',
                                           args=["bc1a602a913db2ab48fbf5b1a9"
                                                 "e1269a", ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode("utf-8"),
                         "\"No Records Available\"")

    def test_return_nothing_if_list_members_all_expired(self):
        ce1 = CacheEntryFactory.create(expiry_date=datetime.date.today() -
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_iterations": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        ce2 = CacheEntryFactory.create(expiry_date=datetime.date.today() -
                                       datetime.timedelta(
                                       days=settings.CACHE_EXPIRY_PERIOD),
                                       md5="ac1a602a913db2ab48fbf5b1a9e1269a",
                                       data={"-num_cores": 20,
                                             "-num_descriptions": 500,
                                             "file_data": self.read_pssm()})
        response = self.client.get(reverse('entryList',
                                           args=["bc1a602a913db2ab48fbf5b1a9"
                                                 "e1269a", ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content.decode("utf-8"),
                         "\"No Records Available\"")
