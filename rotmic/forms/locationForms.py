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
import re
import django.forms as forms

import selectLookups as L
import selectable.forms as sforms

import rotmic.models as M
import componentForms as CF
    
class LocationForm(forms.ModelForm):
    """Customized Form for Location add / change"""
    
    class Meta:
        model = M.Location
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            'temperature' : forms.TextInput(attrs={'size':3}),
            'room' : forms.TextInput(attrs={'size':10}),
            }


class RackForm(forms.ModelForm):
    """Customized Form for Location add / change"""
    
    class Meta:
        model = M.Rack
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'name' : forms.TextInput(attrs={'size':25}),
            }


class ContainerForm(forms.ModelForm, CF.CleaningMixIn):
    """Customized Form for Location add / change"""
    
    ex_id = re.compile('[a-zA-Z_\-0-9\.]{3,}')
    msg_id = 'ID must be >= 3 characters and only contain: a..z, 0..9, ., _, -'
    
    class Meta:
        model = M.Container
        widgets = { ## customize widget dimensions and include dynamic select widgets
            'displayId' : forms.TextInput(attrs={'size':10}),
            'rack' : sforms.AutoComboboxSelectWidget(
                lookup_class=L.ContainerRackLookup, allow_new=False),
            'name' : forms.TextInput(attrs={'size':20}),
            }
    