import random
import string
import factory
import factory.fuzzy
import datetime
import pytz
import hashlib

from django.test import TestCase
from django.conf import settings

from .models import Cache_entry, File


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


def produce_hash():
    test_seq = random_string(length=240)
    m = hashlib.md5()
    test_hash = m.update(test_seq.encode('utf-8'))
    return(m.hexdigest())


class CacheEntryFactory(factory.DjangoModelFactory):
    uniprotID = "P0" + str(random.randint(0, 9)) + str(random.randint(0, 9)) + \
                str(random.randint(0, 9)) + str(random.randint(0, 9))
    md5 = produce_hash()

    class Meta:
        model = Cache_entry


class FileFactory(factory.DjangoModelFactory):
    cache_entry = CacheEntryFactory.create()
    accessed_count = random.randint(0, 100)
    expiry_date = factory.fuzzy.FuzzyDateTime(
                  datetime.datetime(2008, 1, 1, tzinfo=pytz.utc))
    file_location = "/"+str(factory.LazyAttribute(lambda t: random_string()))
    file_type = File.PSSM
    file_byte_start = random.randint(0, 1000000)
    file_byte_stop = file_byte_start + random.randint(0, 1000000)
    blast_hits = random.randint(0, 1000)

    class Meta:
        model = File
