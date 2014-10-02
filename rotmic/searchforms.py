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
import django.contrib.auth.models as auth
from django.db.models import Q

import forms.selectLookups as L
import selectable.forms as sforms

import rotmic.models as M

class JQueryUIDatepickerWidget(forms.DateInput):
    """Custom widget for JQuery Calendar lookup (more robust than AdminDateWidget)"""
    ## See: http://stackoverflow.com/questions/1450463/django-datetimewidget-not-showing-up
    
    def __init__(self, **kwargs):
        super(forms.DateInput, self).__init__(attrs={"size":10, "class": "dateinput"}, **kwargs)

    class Media:
        css = {"all":("http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/themes/redmond/jquery-ui.css",)}
##        js = ("http://ajax.googleapis.com/ajax/libs/jquery/1.4.3/jquery.min.js",
##              "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery-ui.min.js",)


def linkedSearch(field, subfields=['displayId','name'], lookup='contains'):
    """Generate search function for filter field action parameter"""
    def f(qs, query):
        if not query:
            return qs
        searches = [ '%s__%s__%s' % (field, sub, lookup) for sub in subfields ]
        q = Q()
        for s in searches:
            q = q | Q(**{s:query})
        return qs.filter(q)
    
    return f

class ComponentFilter(F.FilterSet):
    """Base definition for all Component subtypes"""
    
    displayId = F.CharFilter(label='ID', lookup_type='contains')

    name      = F.CharFilter(label='Name', lookup_type='contains')
    
    registeredAt = F.DateTimeFilter(label='Registered before',
                                    widget=JQueryUIDatepickerWidget,
                                    lookup_type='lte')
    
    modifiedAt = F.DateFilter(label='Modified after',
                                widget=JQueryUIDatepickerWidget,
                                lookup_type='gte')
    
    author = F.CharFilter(name='author', label='Author',
                          action=linkedSearch('authors', 
                                subfields=['username','first_name','last_name']))

    project = F.CharFilter(name='projects__name', label='Project name',
                          lookup_type='contains')
    
    description = F.CharFilter(name='description', label='Description',
                               lookup_type='contains')

    filterfields = ['componentType', 
                    'displayId', 'name', 'status', 
                    'registeredBy', 'registeredAt',
                    'modifiedBy','modifiedAt',
                    'author', 'project', 'description']
    


def searchDnaMarkers(qs, query):
    q = Q(markers__name__contains=query) | Q(markers__displayId__contains=query) |\
        Q(vectorBackbone__markers__name__contains=query) |\
        Q(vectorBackbone__markers__displayId__contains=query) |\
        Q(insert__markers__name__contains=query) |\
        Q(insert__markers__displayId__contains=query)
        
    r = qs.filter(q)
    return r

class DnaComponentFilter(ComponentFilter, F.FilterSet):
    
    insertId  = F.CharFilter(name='insert', label='Insert (name or ID)',
                             action=linkedSearch('insert'))

    vector  = F.CharFilter(name='vector', label='Base vector (name or ID)',
                           action=linkedSearch('vectorBackbone'))
    
    marker1  = F.CharFilter(name='marker1', label='Marker 1 (name or ID)',
                            lookup_type='contains',
                            action=searchDnaMarkers)

    marker2  = F.CharFilter(name='marker2', label='Marker 2 (name or ID)',
                            lookup_type='contains',
                            action=searchDnaMarkers)

    class Meta:
        model = M.DnaComponent
        fields = ComponentFilter.filterfields

    def __init__(self, *args, **kwargs):
        super(DnaComponentFilter, self).__init__(*args, **kwargs)

        s = self.filters['status']
        s.extra['choices'] = (('','--Any Status--'),) + s.extra['choices']
        s.extra['initial'] = ''


    
def searchCellMarkers(qs, query):
    q = Q(markers__name__contains=query) | Q(markers__displayId__contains=query) |\
        Q(plasmid__vectorBackbone__markers__name__contains=query) |\
        Q(plasmid__vectorBackbone__markers__displayId__contains=query) |\
        Q(plasmid__insert__markers__name__contains=query) |\
        Q(plasmid__insert__markers__displayId__contains=query)
        
    r = qs.filter(q)
    return r

class CellComponentFilter(ComponentFilter, F.FilterSet):
    
    plasmid  = F.CharFilter(name='plasmid', label='Plasmid (name or ID)',
                           action=linkedSearch('plasmid'))

    marker1  = F.CharFilter(name='marker1', label='Marker 1 (name or ID)',
                            lookup_type='contains',
                            action=searchCellMarkers)

    marker2  = F.CharFilter(name='marker2', label='Marker 2 (name or ID)',
                            lookup_type='contains',
                            action=searchCellMarkers)
    class Meta:
        model = M.CellComponent
        fields = ComponentFilter.filterfields

    def __init__(self, *args, **kwargs):
        super(CellComponentFilter, self).__init__(*args, **kwargs)

        s = self.filters['status']
        s.extra['choices'] = (('','--Any Status--'),) + s.extra['choices']
        s.extra['initial'] = ''
        

def searchOligoTemp(qs, query):
    assert isinstance(query, slice)
    if not query:
        return qs
    q = Q(meltingTemp__gt=query.start, meltingTemp__lt=query.stop)
    return qs.filter(q)

class OligoComponentFilter(ComponentFilter, F.FilterSet):
    
    templates  = F.CharFilter(name='template', label='Template (name or ID)',
                              action=linkedSearch('templates'))
    
    reverse = F.CharFilter(name='reversePrimer', label='Reverse Primer (name or ID)',
                           action=linkedSearch('reversePrimers'))
    
    meltingTemp = F.RangeFilter(name='meltingTemp', label='melting Temp. between',
                                action=searchOligoTemp)

    class Meta:
        model = M.OligoComponent
        fields = ComponentFilter.filterfields + ['purification']

    def __init__(self, *args, **kwargs):
        super(OligoComponentFilter, self).__init__(*args, **kwargs)

        s = self.filters['status']
        s.extra['choices'] = (('','--Any Status--'),) + s.extra['choices']
        s.extra['initial'] = ''
        
        s = self.filters['purification']
        s.extra['choices'] = (('','--Any Purification--'),) + s.extra['choices']
        s.extra['initial'] = ''


class ProteinComponentFilter(ComponentFilter, F.FilterSet):
    
    class Meta:
        model = M.ProteinComponent
        fields = ComponentFilter.filterfields

    def __init__(self, *args, **kwargs):
        super(ProteinComponentFilter, self).__init__(*args, **kwargs)

        s = self.filters['status']
        s.extra['choices'] = (('','--Any Status--'),) + s.extra['choices']
        s.extra['initial'] = ''


class ChemicalComponentFilter(ComponentFilter, F.FilterSet):
    
    cas  = F.CharFilter(label='C.A.S.', lookup_type='contains')
    
    class Meta:
        model = M.ChemicalComponent
        fields = ComponentFilter.filterfields

    def __init__(self, *args, **kwargs):
        super(ChemicalComponentFilter, self).__init__(*args, **kwargs)

        s = self.filters['status']
        s.extra['choices'] = (('','--Any Status--'),) + s.extra['choices']
        s.extra['initial'] = ''
