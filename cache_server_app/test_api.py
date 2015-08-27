from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIClient
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request

from .api import SubmissionDetails
from .models import *
from .model_factories import *


class CacheEntryTests(APITestCase):

    def test_get_returns_entry(self):
        ce = CacheEntryFactory.create()
        f1 = FileFactory(cache_entry=ce)
        print(f1)
