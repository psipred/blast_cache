import random
import string
import factory
import factory.fuzzy
import datetime
import pytz
import hashlib
from sortedcontainers import SortedDict

from django.test import TestCase
from django.conf import settings

from .models import Cache_entry


def random_string(length=10):
    return u''.join(random.choice(string.ascii_letters) for x in range(length))


def produce_sequence_hash():
    test_seq = random_string(length=240)
    m = hashlib.md5()
    test_hash = m.update(test_seq.encode('utf-8'))
    return(m.hexdigest())


def read_file(type):
    path = settings.USER_PSSM
    if type == 2:
        path = settings.USER_CHK
    data = ''
    with open(path, 'r') as myfile:
        data = myfile.read()
    return(data)


def produce_settings_hash(data):
    m = hashlib.md5()
    test_hash = m.update(str(SortedDict(data)).encode('utf-8'))
    return(m.hexdigest())


class CacheEntryFactory(factory.DjangoModelFactory):
    name = random_string(length=20)
    md5 = produce_sequence_hash()
    accessed_count = random.randint(0, 100)
    expiry_date = factory.fuzzy.FuzzyDateTime(
                  datetime.datetime(2008, 1, 1, tzinfo=pytz.utc))
    file_type = random.randint(1, 1)
    blast_hit_count = random.randint(0, 5000)
    runtime = random.randint(0, 600)
    data = {"-num_iterations": random.randint(1, 6),
            "-num_descriptions": random.randint(1, 5000),
            "file_data": read_file(file_type)}
    sequence = random_string(length=120)
    blocked = True

    class Meta:
        model = Cache_entry
