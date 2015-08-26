from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import Cache_entry, File


class CacheEntryForm(forms.ModelForm):

    class Meta:
        model = Cache_entry
        fields = ('uniprotID', 'md5')


class FileForm(forms.ModelForm):

    class Meta:
        model = File
        fields = ('file_location', 'file_type', 'file_byte_start',
                  'file_byte_stop', 'blast_hits')
