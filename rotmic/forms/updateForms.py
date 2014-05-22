## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 - 2014 Raik Gruenberg

## This file is part of the rotmic project (https://github.com/graik/rotmic).
## rotmic is free software: you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.

## rotmic is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
## You should have received a copy of the GNU Affero General Public
## License along with rotmic. If not, see <http://www.gnu.org/licenses/>.
from datetime import datetime
import re, copy

import django.forms as forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget
from django.contrib import admin, messages

import selectable.forms as sforms

import selectLookups as L
import rotmic.initialTypes as T

import rotmic.models as M

class UpdateManyForm(forms.Form):
    
    lookups = {M.DnaComponent : L.DnaLookup,
               M.CellComponent : L.SampleCellLookup,
               M.OligoComponent : L.OligoLookup,
               M.ChemicalComponent : L.ChemicalLookup,
               M.ProteinComponent : L.ProteinLookup }
    
    entries = forms.ModelMultipleChoiceField(M.Component.objects.all(), 
                        cache_choices=False, 
                        required=True, 
                        initial=None, 
                        help_text='Start typing ID or name to restrict the choice.\n')
    
    def __init__(self, *arg, **kwarg):
        self.request = kwarg.pop('request')
        self.model = kwarg.pop('model', None)

        self.model_admin = admin.site._registry[self.model]
        self.model_form = self.model_admin.form

        super(UpdateManyForm, self).__init__(*arg, **kwarg)

        f = self.fields['entries']
        
        f.queryset = self.model.objects.all()
        f.widget = sforms.AutoComboboxSelectMultipleWidget(lookup_class=self.lookups[self.model])
        f.label = self.model._meta.verbose_name + 's'
        
        self.build_fields()
        
        if self.request.method == 'GET':
            entries = self.model.objects.select_related().filter(pk__in=self.initial['entries'])
            self.populate_fields(entries)
            
        if self.request.method == 'POST':
            entries = f.widget.value_from_datadict(self.data, self.files, 'entries')
            entries = self.model.objects.filter(pk__in=entries)
            self.populate_fields(entries)

        
    def build_fields(self):
        """add fields according to model admin definitions"""
        a = self.model_admin
        
        for fs in a.fieldsets:
            title, d = fs
            for fieldrow in d['fields']:
                for fieldname in fieldrow:
                    if not fieldname in a.no_update:
                        self.fields[fieldname] = copy.copy(a.form.base_fields[fieldname])
                        self.fields[fieldname].required = False

    def __deduplicate(self, values):
        return [values[i] for i in range(len(values)) if i == 0 or values[i] != values[i-1]]

    def extract_values(self, entries, fieldname):
        """
        Helper function, get all values of given field from list of objects
        """
        if isinstance( self.model_form.base_fields[fieldname], forms.models.ModelMultipleChoiceField):
            ## the more tricky case of RelatedManagers populated with
            ## more than one reference
            values = [ getattr(e, fieldname) for e in entries ]
            values = [ list(v.order_by('id').values_list('id', flat=True)) for v in values ]
            return values
        
        if isinstance( self.model_form.base_fields[fieldname], forms.fields.MultipleChoiceField):
            ## untested!!!
            values = [ getattr(e, fieldname) for e in entries ]
            values = [ ordered(v) for v in values ]
            return values
            
        values = entries.values_list(fieldname, flat=True)
        if len(values) == entries.count():
            return values
        
        raise LookupError, 'Cannot extract values for field ' + fieldname

        
    def populate_fields(self, entries):
        """Fill in values that are the same in all entries"""
        ## get selected entries and already pre-fetch all ForeignKey related objects

        for fieldname in self.fields:
            if fieldname != 'entries':
                ## check for all-equal values and, if yes, copy value -> initial
                values = self.extract_values(entries, fieldname)
                f = self.fields[fieldname]

                if len(values) == entries.count() and\
                   len(self.__deduplicate(values)) <= 1:                   
                    f.all_equal = True
                    f.help_text = 'This field seems to have the same (or no) value in all %i entries.\n' % len(values)\
                        + f.help_text
                    v = values[0]
                    
                    ## don't set empty empty fields;
                    if v:
                        self.initial[fieldname] = v
                else:
                    f.all_equal = False
                    f.help_text = 'Attention! This field currently has different values in the selected entries. Only change if you are sure.\n'\
                        + f.help_text


    def add_error(self, field, msg):
        """
        This method exists in Form from django 1.7+ ; remove/rename after upgrade
        """
        self._errors[field] = self._errors.get( field, self.error_class([]) )
        if len( self._errors[field] ) < 3:
            self._errors[field].append(msg)
        elif len( self._errors[field] ) == 3:
            self._errors[field].append('...skipping further errors.')
 
    def delta(self, data, entries):
        pass

    def get_forms(self):
        """create a single input form for every entry, to be called *after* clean"""
        entries = self.cleaned_data['entries']
        
        if 'entries' in self.changed_data:
            self.changed_data.remove('entries')
            
        cleaned = self.cleaned_data

        fields_changed = self.delta(cleaned, entries)

        d = { k : self.fields[k].prepare_value(cleaned[k]) for k in self.changed_data }
        
        entry_forms = []
        for e in entries:
            
            try:
                data = forms.model_to_dict(e)
                data.update(d)
                
                form = self.model_form( data, instance=e )
                form.request = self.request  ##This is actually only required for forms derrived from SampleForm
                
                if not form.is_valid(): raise ValueError('single form validation')

                entry_forms += [form]

            except ValueError as error:
                for field, msg in form.errors.items():
                    s = unicode(form.instance) + ': ' + msg[0]
                    self.add_error(field, s)
        
        return entry_forms