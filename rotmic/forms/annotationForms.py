## Rotten Microbes (rotmic) -- Laboratory Sequence and Sample Management
## Copyright 2013 Raik Gruenberg

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
from django.forms.models import inlineformset_factory
from django.http import HttpResponseRedirect

from rotmic.models import DnaAnnotation, DnaComponent

class SingleDnaAnnotationForm(forms.ModelForm):
    """Form for a single annotation -- to be used within a ModelFormset"""
    
    class Meta:
        model = DnaAnnotation
        fields = ['subComponent', 'bioStart', 'bioEnd', 'hardLink', 'strand']


DnaAnnotationFormSet = inlineformset_factory(
    DnaComponent, DnaAnnotation, 
    fk_name='parentComponent',
    form=SingleDnaAnnotationForm,
    extra=2,
    )

