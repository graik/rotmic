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

from rotmic.forms.componentForms import ComponentForm, getComponentWidgets
import models as M

import rotmic.forms.selectLookups as L
import selectable.forms as sforms

class AssemblyProjectForm(ComponentForm):
    
    class Meta:
        model = M.AssemblyProject
        widgets = getComponentWidgets({
            'description' : forms.Textarea(attrs={'cols': 100, 'rows': 3,
                                             'style':'font-family:monospace'}),
        })
        
class AssemblyPartForm(forms.ModelForm):
    
    partId = forms.CharField(max_length=2, label='ID',
                             widget=forms.TextInput(attrs={'style':'width:10px'}))
    
    class Meta:
        model = M.AssemblyLink
        widgets = {'component' : sforms.AutoComboboxSelectWidget(
                                    lookup_class=L.DnaLookup,
                                    allow_new=False),
                   'sequence' : forms.Textarea(attrs={'cols': 40, 'rows': 2,
                                             'style':'font-family:monospace'}),
                   'bioStart' : forms.TextInput(attrs={'size':3}),
                   'bioEnd' : forms.TextInput(attrs={'size':3}),
                   }

    class Media: 
        js = ['inline_ordering.js', ]
        
    def __init__(self, *args, **kwargs):
        super(AssemblyPartForm, self).__init__(*args, **kwargs)

        # supress Plus link for new object creation
        self.fields['component'].widget.can_add_related = False
    

class AssemblyForm(forms.ModelForm):
    
    class Meta:
        model = M.Assembly
    
    class Media:
        js = ['inline_ordering.js']
        
