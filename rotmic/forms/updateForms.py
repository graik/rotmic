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
import re

import django.forms as forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import AdminDateWidget

import selectable.forms as sforms

import selectLookups as L
import rotmic.initialTypes as T

import rotmic.models as M

class UpdateManyForm(forms.Form):
    
    lookups = {M.DnaComponent : L.DnaLookup,
               M.OligoComponent : L.OligoLookup,
               M.ChemicalComponent : L.ChemicalLookup,
               M.ProteinComponent : L.ProteinLookup }
    
    entries = forms.ModelMultipleChoiceField(M.Component.objects.all(), 
                        cache_choices=False, 
                        required=True, 
                        initial=None, 
                        help_text='Start typing ID to restrict the choice.\n')
    
    def __init__(self, *arg, **kwarg):
        self.request = kwarg.pop('request')
        self.model = kwarg.pop('model', None)

        super(UpdateManyForm, self).__init__(*arg, **kwarg)
        
        f = self.fields['entries']
        
        f.widget = sforms.AutoComboboxSelectMultipleWidget(lookup_class=self.lookups[self.model])
        f.label = self.model._meta.verbose_name + 's'
        
    def add_error(self, field, msg):
        """
        This method exists in Form from django 1.7+ ; remove/rename after upgrade
        """
        self._errors[field] = self._errors.get( field, self.error_class([]) )
        if len( self._errors[field] ) < 3:
            self._errors[field].append(msg)
        elif len( self._errors[field] ) == 3:
            self._errors[field].append('...skipping further errors.')
 
