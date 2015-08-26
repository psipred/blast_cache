import os
import django
import hashlib

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'cache_server.settings.dev')

django.setup()

from cache_server_app.models import Cache_entry, File


def populate():
    Cache_entry.objects.all().delete()
    File.objects.all().delete()

    test_seq = 'MLELLPTAVEGVSQAQITGRPEWIWLALGTALMGLGTLYFLVKGMGVSDPDAKKFYAI' + \
               'LVPAIAFTMYLSMLLGYGLTMVPFGGEQNPIYWARYADWLFTTPLLLLDLALLVDADQ' + \
               'ILALVGADGIMIGTGLVGALTKVYSYRFVWWAISTAAMLYILYVLFFGFTSKAESMRP' + \
               'ASTFKVLRNVTVVLWSAYPVVWLIGSEGAGIVPLNIETLLFMVLDVSAKVGFGLILLR' + \
               'AIFGEAEAPEPSAGDGAAATSD'
    m = hashlib.md5()
    test_hash = m.update(test_seq.encode('utf-8'))
    this_cache_entry = add_cache_entry(uniprotID="P012345", md5=m.hexdigest())

    this_file_entry = add_file(ce=this_cache_entry,
                               file_location="/tmp",
                               file_type=1,
                               start=0,
                               stop=1000000,
                               hits=500)


def add_cache_entry(uniprotID, md5):
    ce = Cache_entry.objects.create(uniprotID=uniprotID)
    ce.md5 = md5
    ce.save()
    return(ce)


def add_file(ce, file_location, file_type, start, stop, hits):
    f = File.objects.create(cache_entry=ce)
    f.accessed_count = 0
    # f.expiry_date = "2015-08-25"
    f.file_location = file_location
    f.file_type = file_type
    f.file_byte_start = start
    f.file_byte_stop = stop
    f.blast_hits = hits
    f.save()
    return(f)

# Start execution here!
if __name__ == '__main__':
    print("Starting population script...")
    populate()
