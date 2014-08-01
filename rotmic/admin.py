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

from django.contrib import admin
import django.utils.html as html
from django.utils.safestring import mark_safe

import reversion

import rotmic.models as M

from .utils.customadmin import ViewFirstModelAdmin
from .utils import adminFilters as filters

from . import forms
from .forms import selectLookups as L

from .adminBase import UserRecordMixin, UserRecordProtectedMixin, \
     RequestFormMixin, export_csv, UpdateManyMixin

from . import adminUser  ## trigger extension of User
from . import adminComponents ## trigger registration of component admin interfaces
from . import adminProjects ## trigger registration of ProjectAdmin
from . import adminSamples ## trigger registration of Sample-related admin interfaces


class DnaComponentTypeAdmin( reversion.VersionAdmin ):
    
    fieldsets = (
        (None, {
            'fields': (('name', 'subTypeOf',),
                       ('description', 'isInsert',),
                       ('uri',),
                       )
            }
         ),
        )
    
    list_display = ('__unicode__','subTypeOf', 'description', 'isInsert')
    list_display_links = ('__unicode__',)
    list_editable = ('isInsert',)
    
    list_filter = ('subTypeOf', 'isInsert')
                       

admin.site.register(M.DnaComponentType, DnaComponentTypeAdmin)


class CellComponentTypeAdmin( reversion.VersionAdmin):
    
    fieldsets = (
        (None, {
            'fields': (('name', 'subTypeOf',),
                       ('description',),
                       ( 'allowPlasmids', 'allowMarkers'),
                       ('uri',),
                       )
            }
         ),
        )
    
    list_display = ('__unicode__','subTypeOf', 'description', 'allowPlasmids', 
                    'allowMarkers')
    list_display_links = ('__unicode__',)
    list_editable = ('allowPlasmids','allowMarkers')
    
    list_filter = ('subTypeOf', 'allowPlasmids', 'allowMarkers')

admin.site.register(M.CellComponentType, CellComponentTypeAdmin)
    

class OligoComponentTypeAdmin( reversion.VersionAdmin):
    
    fieldsets = (
        (None, {
            'fields': (('name', ),
                       ('description',),
                       ('uri',),
                       )
            }
         ),
        )
    
    list_display = ('__unicode__', 'description')
    list_display_links = ('__unicode__',)

admin.site.register(M.OligoComponentType, OligoComponentTypeAdmin)

class ChemicalTypeAdmin( reversion.VersionAdmin ):
    
    fieldsets = (
        (None, {
            'fields': (('name', 'subTypeOf'),
                       ('description',),
                       ('uri',),
                       )
            }
         ),
        )
    
    list_display = ('__unicode__', 'subTypeOf', 'description')
    list_filter = ('subTypeOf',)

    list_display_links = ('__unicode__',)

admin.site.register(M.ChemicalType, ChemicalTypeAdmin)


class ProteinComponentTypeAdmin( reversion.VersionAdmin ):
    
    fieldsets = (
        (None, {
            'fields': (('name', 'subTypeOf'),
                       ('description',),
                       ('uri',),
                       )
            }
         ),
        )
    
    list_display = ('__unicode__', 'subTypeOf', 'description')
    list_filter = ('subTypeOf',)

    list_display_links = ('__unicode__',)

admin.site.register(M.ProteinComponentType, ProteinComponentTypeAdmin)


class UnitAdmin( reversion.VersionAdmin, UpdateManyMixin):
    
    fieldsets = (
        (None, {
            'fields': (('name', 'unitType',),
                       ('conversion',),
                       )
            }
         ),
        )

    actions = ['make_update']
    exclude_from_update = ['name']
    model_lookup = L.UnitLookup
    
    list_display = ('name','unitType', 'conversion')
    list_filter = ('unitType',)
    
admin.site.register( M.Unit, UnitAdmin )



class LocationAdmin(UserRecordMixin, reversion.VersionAdmin, ViewFirstModelAdmin, UpdateManyMixin):
    form = forms.LocationForm
    
    permit_delete = [] ## de-activate author-only delete permission

    change_form_template = 'admin/rotmic/change_form_viewfirst.html'  ## adapt breadcrums to view first admin

    change_list_template = "admin/rotmic/location/change_list.html"

    fieldsets = [
        (None, {
            'fields' : ((('displayId', 'name'),
                         ('temperature','room'),
                        )),
            'description' : 'Describe a freezer, row of shelves or similar storage location.',
            }
         )
        ]

    list_display = ('displayId', 'name', 'showComments',
                    'temperature', 'room',
                    'showRackCount', 'showContainerCount', 'showSampleCount', 
                    'showEdit')
    list_filter = ('room', 'temperature')
    search_fields = ('displayId', 'name',)

    save_as = True
    
    actions = ['make_update']
    exclude_from_update = ['displayId']
    model_lookup = L.LocationLookup
    
admin.site.register( M.Location, LocationAdmin )


class RackAdmin(UserRecordMixin, reversion.VersionAdmin, ViewFirstModelAdmin, UpdateManyMixin):
    form = forms.RackForm

    permit_delete = [] ## de-activate author-only delete permission

    change_form_template = 'admin/rotmic/change_form_viewfirst.html'  ## adapt breadcrums to view first admin
    
    change_list_template = "admin/rotmic/rack/change_list.html"

    fieldsets = [
        (None, {
            'fields' : ((('displayId', 'location', 'name'),
                        )),
            'description' : 'Describe a freezer rack, single shelve or similar holder of containers.'
            }
         )
        ]

    list_display = ('displayId', 'name', 'showComments',
                    'showLocationUrl', 
                    'showContainerCount', 'showSampleCount',
                    'showEdit')
    list_filter = (filters.RackLocationFilter,)
    search_fields = ('displayId', 'name', 'location__displayId', 'location__name')

    save_as = True

    actions = ['make_update']
    exclude_from_update = ['displayId']
    model_lookup = L.RackLookup

    def showLocationUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, M.Rack), 'object missmatch'
        x = obj.location
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="">%s</a>' \
                              % (url, unicode(x)) )
    showLocationUrl.allow_tags = True
    showLocationUrl.short_description = 'Location'
    

admin.site.register( M.Rack, RackAdmin )


class ContainerAdmin(UserRecordProtectedMixin, reversion.VersionAdmin, ViewFirstModelAdmin, UpdateManyMixin):
    form = forms.ContainerForm

    permit_delete = [] ## de-activate author-only delete permission
    
    change_form_template = 'admin/rotmic/change_form_viewfirst.html'  ## adapt breadcrums to view first admin

    change_list_template = "admin/rotmic/container/change_list.html"

    fieldsets = [
        (None, {
            'fields' : ((('displayId', 'rack', 'name'),
                         ('containerType',),
                         ('description',),
                        )),
            'description' : 'Describe a sample container or box.'
            }
         )
        ]

    list_display = ('__unicode__', 'showComments', 'showRackUrl', 'showLocationUrl', 'containerType', 
                    'showSampleCount',
                    'showEdit')
                    
    list_filter =  ('containerType', filters.ContainerLocationFilter, 
                    filters.ContainerRackFilter)
    search_fields = ('displayId', 'name','description')

    save_as = True

    actions = ['make_update']
    exclude_from_update = ['displayId']
    model_lookup = L.SampleContainerLookup

    def showLocationUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, M.Container), 'object missmatch'
        x = obj.rack.location
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="">%s</a>' \
                              % (url, unicode(x)) )
    showLocationUrl.allow_tags = True
    showLocationUrl.short_description = 'Location'

    def showRackUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, M.Container), 'object missmatch'
        x = obj.rack
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="">%s</a>' \
                              % (url, unicode(x)) )
    showRackUrl.allow_tags = True
    showRackUrl.short_description = 'Rack'

admin.site.register( M.Container, ContainerAdmin )


class SampleProvenanceTypeAdmin(reversion.VersionAdmin):
    
    list_display = ('name','isDefault', 'requiresSource', 'description')
    list_filter = ('requiresSource',)
    
admin.site.register( M.SampleProvenanceType, SampleProvenanceTypeAdmin )
    

class SequencingRunInline(admin.TabularInline):
    model = M.SequencingRun
    form = forms.SequencingRunForm
    extra = 2
    max_num = 15

    fieldsets = (
        (None,
         { 'fields': ('f', 'primer', 'description')
           }),
    )
    
class SequencingAdmin(UserRecordProtectedMixin, RequestFormMixin, reversion.VersionAdmin):
    form = forms.SequencingForm
    
    permit_delete = [] ## de-activate author-only delete permission
    
    change_list_template = "admin/rotmic/sequencing/change_list.html"

    inlines = [ SequencingRunInline ]

    fieldsets = (
        (None,
         { 'fields': (('dummyfield',), ('sample','evaluation'),('orderedAt', 'orderedBy'), 
                      'comments')
           }),
    )

    ordering = ('sample', 'orderedAt')

    date_hierarchy = 'orderedAt'
    
    save_as = True
    save_on_top = True

    list_display   = ( '__unicode__', 'showSample', 'orderedAt', 'orderedBy', 'showEvaluation' )

    list_filter    = ('sample__dna__projects', filters.SortedOrderedByFilter, 'evaluation',)

    search_fields  = ('sample__displayId', 'sample__name', 'registeredBy__username',
                      'comments','evaluation',
                      'orderedBy__username',
                      'sample__container__displayId')
    
    def showSample(self, obj):
        """Table display of linked sample ''"""
        assert isinstance(obj, M.Sequencing), 'object missmatch'
        x = obj.sample
        if not x:
            return u''
        url = x.get_absolute_url()
        s = '%s (%s)' % ( x, x.content.displayId)
        return html.mark_safe('<a href="%s" title="">%s</a>' \
                              % (url, s ))
    showSample.allow_tags = True
    showSample.short_description = 'Sample'

admin.site.register(M.Sequencing, SequencingAdmin)