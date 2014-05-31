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

from rotmic.models import SequenceLink, DnaComponent

class SingleSequenceLinkForm(forms.ModelForm):
    """Form for a single annotation -- to be used within a ModelFormset"""
    
    class Meta:
        model = SequenceLink
        fields = ['subComponent', 'bioStart', 'bioEnd', 'hardLink', 'strand']


DnaAnnotationFormSet = inlineformset_factory(
    DnaComponent, SequenceLink, 
    fk_name='component',
    form=SingleSequenceLinkForm,
    extra=2,
    )

# Note: instruction for JS adding extra formsets on the fly:
# http://www.lab305.com/news/2012/jul/19/django-inline-formset-underscore/
# http://stackoverflow.com/questions/21260987/add-a-dynamic-form-to-a-django-formset-using-javascript-in-a-right-way