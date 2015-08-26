from django.contrib import admin

# Register your models here.
from .models import Cache_entry, File


class FileInline(admin.TabularInline):
    list_diplay = ('pk', 'accessed_count', 'expiry_date', 'file_location',
                   'file_type', 'file_byte_start', 'file_byte_stop',
                   'blast_hits')
    model = File
    extra = 3


class CacheEntryAdmin(admin.ModelAdmin):
    inlines = [FileInline, ]
    list_diplay = ('pk', 'uniprotID', 'md5')


admin.site.register(Cache_entry, CacheEntryAdmin)
