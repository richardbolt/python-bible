from django import forms
from django.db import models
from django.core import exceptions
from __init__ import Verse

class VerseFormField(forms.Field):
    def clean(self, value):
        """Form field for custom validation entering verses"""
        
        try:
            verse = Verse(value)
        except:
            raise forms.ValidationError('no!')
        
        # return the cleaned and processed data
        return verse.to_string()


class VerseField(models.Field):
    description = "A scripture reference to a specific verse"
    empty_strings_allowed = False
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 104
        super(VerseField, self).__init__(*args, **kwargs)
    
    def db_type(self):
            return 'char(%s)' % self.max_length
    
    def get_internal_type(self):
        return "VerseField"
    
    def to_python(self, value):
        if value is None:
            return value
        
        try:
            return Verse(value)
        except:
            exceptions.ValidationError('no!')
    
    def get_db_prep_lookup(self, lookup_type, value):
        # For "__book", "__chapter", and "__verse" lookups, convert the value
        # to an int so the database backend always sees a consistent type.
        if lookup_type in ('book', 'verse', 'chapter'):
            return [int(value)]
        return super(VerseField, self).get_db_prep_lookup(lookup_type, value)
    
    def get_db_prep_value(self, value):
        # Casts dates into a string for saving to db
        return value.to_string()
    
    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
    
    def formfield(self, **kwargs):
        defaults = {'form_class': VerseFormField}
        defaults.update(kwargs)
        return super(VerseField, self).formfield(**defaults)
        
v = Verse('rom1:1')
print v