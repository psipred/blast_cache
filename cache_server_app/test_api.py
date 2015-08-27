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
        print(ce.md5)
        response = self.client.get(reverse('cacheDetail',
                                           args=[ce.md5, ]) + ".json")
        print(reverse('cacheDetail', args=[ce.md5, ]))
        response.render()
        self.assertEqual(response.status_code, 200)
        # test_data = '{"count":2,"next":null,"previous":null,' \
        #             '"results":[{"pk":2,"name":"job1"},{"pk":3,"name":"job2"}]}'
        # self.assertEqual(response.content.decode("utf-8"), test_data)

        print(f1)
