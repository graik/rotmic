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
import django.forms as forms

from .componentForms import ComponentForm, getComponentWidgets
import rotmic.models as M

import selectLookups as L
import selectable.forms as sforms

class DnaAssemblyForm(ComponentForm):
    
    class Meta:
        model = M.DnaAssembly
        widgets = getComponentWidgets({
            'description' : forms.Textarea(attrs={'cols': 100, 'rows': 3,
                                             'style':'font-family:monospace'}),
        })
        
class AssemblyLinkForm(forms.ModelForm):
    
    class Meta:
        model = M.AssemblyLink
        widgets = {'component' : sforms.AutoComboboxSelectWidget(
                                    lookup_class=L.DnaLookup,
                                    allow_new=False),
                   'sequence' : forms.Textarea(attrs={'cols': 50, 'rows': 2,
                                             'style':'font-family:monospace'})
                   }

    class Media: 
        js = ['inline_ordering.js', ]
