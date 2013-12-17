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
import itertools

from django import forms

## third-party ForeignKey lookup field
from selectable.base import ModelLookup
from selectable.registry import registry
import selectable.forms as sforms

import rotmic.models as M
import rotmic.initialTypes as T
import rotmic.initialUnits as U
import rotmic.initialComponents as IC


class FixedSelectMultipleWidget( sforms.AutoComboboxSelectMultipleWidget ):
    """
    Bug fix the change detection method;
    This should, in theory, be obsolete since Django 1.6
    (The _has_changed method has moved from widget to FormField)
    """    
    def _has_changed(self,initial, data):
        """override buggy method from SelectWidget"""
        old_values = [ unicode(i) for i in (initial or [u''])]
        new_values = [ unicode(i) for i in (data or [u''])]
        return not set(new_values) == set(old_values)


class DnaLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(DnaLookup)

class OligoLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.OligoComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(OligoLookup)

class ChemicalLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.ChemicalComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(ChemicalLookup)


class InsertLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    filters = {'componentType__subTypeOf': T.dcFragment,
               'componentType__isInsert' : True}
    
    def get_item_id(self,item):
        return item.pk

registry.register(InsertLookup)


class VectorLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    
    filters = {'componentType__subTypeOf': T.dcVectorBB }
    
    def get_query(self, request, term):
        """
        Special case: sort 'unknown vector' to top.
        See: http://stackoverflow.com/questions/431628/how-to-combine-2-or-more-querysets-in-a-django-view
        """
        q = super(VectorLookup, self).get_query(request, term)

        rest = q.exclude(id=IC.vectorUnknown.id)
        unknown = q.filter(id=IC.vectorUnknown.id)
        
        r = list(itertools.chain(unknown, rest))
        return r    
    
    def get_item_id(self,item):
        return item.pk

registry.register(VectorLookup)


class PlasmidLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf': T.dcPlasmid }
    
    def get_item_id(self,item):
        return item.pk

registry.register(PlasmidLookup)


class MarkerLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf': T.dcMarker }
    
    def get_item_id(self,item):
        return item.pk

registry.register(MarkerLookup)

class SampleDnaLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.DnaComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    filters = {'componentType__subTypeOf__in': [T.dcPlasmid, T.dcFragment] }
    
    def get_item_id(self,item):
        return item.pk

registry.register(SampleDnaLookup)

class SampleCellLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.CellComponent
    search_fields = ('displayId__startswith', 'name__icontains')
    ##filters = {'componentType__subTypeOf__in': [T.dcPlasmid, T.dcFragment] }
    
    def get_item_id(self,item):
        return item.pk

registry.register(SampleCellLookup)


class SampleContainerLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.Container
    search_fields = ('rack__displayId__startswith',
                     'displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register(SampleContainerLookup)


class ContainerRackLookup(ModelLookup):
    """for selectable auto-completion field in Container form"""
    model = M.Rack
    search_fields = ('displayId__startswith', 'name__icontains')
    
    def get_item_id(self,item):
        return item.pk

registry.register( ContainerRackLookup )


class UnitLookup(ModelLookup):
    """Lookup definition for selectable auto-completion fields"""
    model = M.Unit
    search_fields = ('name__startswith', )
    
    def get_query(self, request, term):
        """Special case: replace 'u' by \micro during autocomplete"""
        r = super(UnitLookup, self).get_query(request, term)
        
        if 'u' in term:
            microterm = term.replace('u',u"\u00B5")
            r = r | super(UnitLookup, self).get_query(request, microterm)
        return r    

    def get_item_id(self,item):
        return item.pk


class ConcentrationUnitLookup(UnitLookup):
    """Limit choices to concentration units"""
    def get_query(self, request, term):
        r = super(ConcentrationUnitLookup, self).get_query(request, term)
        return r.filter(unitType='concentration')
    
registry.register(ConcentrationUnitLookup)

class AmountUnitLookup(UnitLookup):
    """Limit choices to amount units"""
    def get_query(self, request, term):
        r = super(AmountUnitLookup, self).get_query(request, term)
        r = r.filter(unitType__in=['volume', 'mass','number'])
        return r

registry.register(AmountUnitLookup)

class VolumeAmountUnitLookup(UnitLookup):
    """Limit choices to Volume units"""
    def get_query(self, request, term):
        r = super(VolumeAmountUnitLookup, self).get_query(request, term)
        r = r.filter(unitType='volume')
        return r

registry.register(VolumeAmountUnitLookup)

