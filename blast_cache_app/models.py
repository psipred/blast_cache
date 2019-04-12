from datetime import date
from dateutil.relativedelta import relativedelta

from django.contrib.postgres.fields import HStoreField
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


class Cache_entry (TimeStampedModel):
    PSSM = 1
    MTX = 2
    FILE_CHOICES = (
        (PSSM, "pssm"),
        (MTX, "mtx"),
    )
    name = models.CharField(max_length=128, unique=False, null=True,
                            blank=False, db_index=True)
    md5 = models.CharField(max_length=64, unique=False, null=False,
                           blank=False, db_index=True)
    # hash of the blast sequence
    accessed_count = models.IntegerField(default=0, null=False, blank=False)
    expiry_date = models.DateField(auto_now_add=False)  # set on save
    file_type = models.IntegerField(null=True, blank=False,
                                    choices=FILE_CHOICES, default=MTX)
    blast_hit_count = models.IntegerField(default=0, null=False, blank=False)
    runtime = models.IntegerField(default=0, null=False, blank=False)
    data = HStoreField(null=True, )  # we store the pssm text data and the
    #                                  commandline options here.
    sequence = models.CharField(max_length=65536, unique=False, null=True,
                                blank=False, db_index=True)
    blocked = models.BooleanField(default=False, null=False)

    def __str__(self):
        return str(self.md5)

    class Meta:
        get_latest_by = 'created'
        ordering = ('created', )
