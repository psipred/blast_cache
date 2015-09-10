from datetime import date
from dateutil.relativedelta import relativedelta

from django.db import models


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating ``created``
    and ``modified`` fields.

    use with
    class Flavor(TimeStampedModel):
    """
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Cache_entry (models.Model):
    uniprotID = models.CharField(max_length=20, unique=True, null=False,
                                 blank=False, db_index=True)
    md5 = models.CharField(max_length=64, unique=True, null=False,
                           blank=False, db_index=True)

    def __str__(self):
        return str(self.uniprotID)


class File (TimeStampedModel):
    PSSM = 1
    CHK = 2
    FILE_CHOICES = (
        (PSSM, "pssm"),
        (CHK, "chk"),
        # add more when more backends are complete
    )
    accessed_count = models.IntegerField(default=0, null=False, blank=False)
    expiry_date = models.DateTimeField(auto_now_add=False)
    file_location = models.CharField(max_length=256, null=False,
                                     blank=False, db_index=True)
    file_type = models.IntegerField(null=False, blank=False,
                                    choices=FILE_CHOICES, default=CHK)
    file_byte_start = models.IntegerField(default=0, null=False, blank=False)
    file_byte_stop = models.IntegerField(default=0, null=False, blank=False)
    cache_entry = models.ForeignKey(Cache_entry)
    blast_hits = models.IntegerField(default=0, null=False, blank=False)
    runtime = models.IntegerField(default=0, null=True, blank=False)

    def insert_file_details(ce, file_location, file_type,
                            start, stop, hits, runtime):
        exp_date = date.today() + relativedelta(months=+6)
        f = File.objects.create(cache_entry=ce, expiry_date=exp_date)
        f.accessed_count = 0
        f.file_location = file_location
        f.file_type = file_type
        f.file_byte_start = start
        f.file_byte_stop = stop
        f.blast_hits = hits
        runtime = runtime
        f.save()

    def __str__(self):
        return str(self.pk)

    class Meta:
        get_latest_by = 'created'
