import random
import string
import factory
import factory.fuzzy
import datetime
import pytz
import hashlib

from django.test import TestCase
from django.conf import settings

from .models import Cache_entry


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


def produce_hash():
    test_seq = random_string(length=240)
    m = hashlib.md5()
    test_hash = m.update(test_seq.encode('utf-8'))
    return(m.hexdigest())


def read_file(type):
    path = settings.USER_PSSM
    if type == 2:
        path = settings.USER_CHK
    data = ''
    with open('data.txt', 'r') as myfile:
        data = myfile.read()
    return(data)


class CacheEntryFactory(factory.DjangoModelFactory):
    name = random_string(length=20)
    md5 = produce_hash()
    accessed_count = random.randint(0, 100)
    expiry_date = factory.fuzzy.FuzzyDateTime(
                  datetime.datetime(2008, 1, 1, tzinfo=pytz.utc))
    file_type = random.randint(1, 2)
    blast_hits = random.randint(0, 5000)
    runtime = random.randint(0, 600)
    data = {"-num_iterations": random.randint(1, 6),
            "-num_descriptions": random.randint(1, 5000),
            "file_data": read_file(self.file_type)}

    class Meta:
        model = Cache_entry
