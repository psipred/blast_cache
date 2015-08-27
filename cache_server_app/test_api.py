from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from .api import CacheDetails
from .models import *
from .model_factories import *


class CacheEntryTests(APITestCase):

    def test_get_returns_entry(self):
        ce = CacheEntryFactory.create()
        f1 = FileFactory(cache_entry=ce)
        response = self.client.get(reverse('cacheDetail',
                                           args=[ce.md5, ]) + ".json")
        response.render()
        self.assertEqual(response.status_code, 200)
        date = str(f1.expiry_date)
        date = date[:10] + 'T' + date[11:]
        date = date[:26] + 'Z'
        test_data = '{{"uniprotID":"{0}","md5":"{1}",'.format(ce.uniprotID,
                                                              ce.md5)
        test_data += '"file_set":[{{"accessed_count":{0},'.format(f1.accessed_count)
        test_data += '"expiry_date":"{0}","file_type":{1},'.format(date, f1.file_type)
        test_data += '"blast_hits":{0}}}]}}'.format(f1.blast_hits)
        self.assertEqual(response.content.decode("utf-8"), test_data)
