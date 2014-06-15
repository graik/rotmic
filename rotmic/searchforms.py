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
import django_filters as F

import django.forms as forms

import rotmic.models as M

class JQueryUIDatepickerWidget(forms.DateInput):
    def __init__(self, **kwargs):
        super(forms.DateInput, self).__init__(attrs={"size":10, "class": "dateinput"}, **kwargs)

    class Media:
        css = {"all":("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/themes/redmond/jquery-ui.css",)}
##        js = ("http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js",
##              "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery-ui.min.js",)

class ComponentFilter(F.FilterSet):
    
    displayId = F.CharFilter(label='ID', lookup_type='contains',
                             help_text='(part of unique ID)')

    name      = F.CharFilter(label='Name', lookup_type='contains')
    
    

    registeredAt = F.DateTimeFilter(label='Registered before',
                                    widget=JQueryUIDatepickerWidget,
                                    lookup_type='lte')
    
    modifiedAt = F.DateFilter(label='Modified after',
                                widget=JQueryUIDatepickerWidget,
                                lookup_type='gte')

    filterfields = ['displayId', 'name', 'status',
                  'registeredBy', 'registeredAt',
                  'modifiedBy','modifiedAt',]
    

class DnaComponentFilter(ComponentFilter, F.FilterSet):
    
    insertId  = F.CharFilter(name='insert__displayId', label='insert ID',
                             lookup_type='contains')

    insertName= F.CharFilter(name='insert__name', label='insert Name',
                             lookup_type='contains')
    
    vectorId  = F.CharFilter(name='vector__displayId', label='vector ID',
                             lookup_type='contains')
    vectorName= F.CharFilter(name='vector__name', label='vector Name',
                             lookup_type='contains')

    class Meta:
        model = M.DnaComponent
        fields = ComponentFilter.filterfields

    def __init__(self, *args, **kwargs):
        super(DnaComponentFilter, self).__init__(*args, **kwargs)

        s = self.filters['status']
        s.extra['choices'] = (('','--Any Status--'),) + s.extra['choices']
        s.extra['initial'] = ''
        
