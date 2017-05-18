from django.contrib import admin

# Register your models here.
from .models import Cache_entry


class CacheEntryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'md5', 'accessed_count', 'created',
                    'modified', 'expiry_date', 'file_type', 'blast_hit_count',
                    'runtime', )


admin.site.register(Cache_entry, CacheEntryAdmin)
