from django import forms
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError

from .models import Cache_entry


class CacheEntryForm(forms.ModelForm):

    class Meta:
        model = Cache_entry
        fields = ('md5', )
