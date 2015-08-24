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
    uniprotID models.CharField(max_length=20, unique=True, null=False,
                               blank=False, db_index=True)
    md5 = models.CharField(max_length=64, unique=True, null=False,
                           blank=False, db_index=True)

    def __str__(self):
        return str(self.uniprotID)


class Pssm (TimeStampedModel):
    accessed_count = models.IntegerField(default=0, null=False, blank=False)
    expiry_date = models.DateTimeField(auto_now_add=True)
    pssm_file = models.FileField(blank=False)
    hit_count = models.IntegerField(default=0, null=False, blank=False)
    cache_entry = models.ForeignKey(Cache_entry)

    def __str__(self):
        return str(self.pk)


class Chk (TimeStampedModel):
    accessed_count = models.IntegerField(default=0, null=False, blank=False)
    expiry_date = models.DateTimeField(auto_now_add=True)
    chk_file = models.FileField(blank=False)
    hit_count = models.IntegerField(default=0, null=False, blank=False)
    cache_entry = models.ForeignKey(Cache_entry)

    def __str__(self):
        return str(self.pk)
