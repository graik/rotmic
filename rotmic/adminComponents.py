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
"""Admin interface for Component and derrived classes"""

import StringIO
from collections import OrderedDict

from django.contrib import admin, messages
from django.utils import safestring, html

import reversion
from Bio import SeqIO

from . import models as M
from . import forms
from . import initialTypes as I
from .templatetags import rotmicfilters as F
from .utils import adminFilters as filters
from .utils import ids
from .utils.customadmin import ViewFirstModelAdmin

from .adminBase import BaseAdminMixin, export_csv

class ComponentAttachmentInline(admin.TabularInline):
    model = M.ComponentAttachment
    form = forms.AttachmentForm
    template = 'admin/rotmic/componentattachment/tabular.html'
    can_delete=True
    extra = 1
    max_num = 5

class ComponentAdmin( ViewFirstModelAdmin ):
    """
    Derived from ViewFirstModelAdmin -- Custom version of admin.ModelAdmin
    which shows a read-only View for a given object instead of the normal
    ChangeForm. The changeForm is accessed by admin/ModelName/id/edit.
    
    In addition, there is extra_context provided to the change_view:
    * dnaTypes -- all registered instances of DnaComponentType
    * cellTypes -- all CellComponentTypes
    * dnaCategories -- all "super" or base-level DnaComponentTypes
    * cellCategories -- all "super" or base-level CellComponentTypes
    
    Component-specific methods:
    * showDescription -- truncated description with html mouse-over full text for tables
    """
    
    def queryset(self, request):
        """
        Return actual sub-class instances instead of generic Component super-class
        This method builds on the custom InheritanceManager replacing Component.objects
        """
        return super(ViewFirstModelAdmin,self).queryset(request).select_subclasses()

    def change_view(self, request, object_id, form_url='', extra_context=None):
        "The 'Edit' admin view for this model."
        extra_context = extra_context or {}
        
        extra_context['dnaTypes'] = M.DnaComponentType.objects.all()
        extra_context['dnaCategories'] = M.DnaComponentType.objects.filter(subTypeOf=None)
        extra_context['cellTypes'] = M.CellComponentType.objects.all()
        extra_context['cellCategories'] = M.CellComponentType.objects.filter(subTypeOf=None)
        
        return super(ComponentAdmin, self).change_view(\
            request, object_id, form_url, extra_context=extra_context)


    def add_view(self, request, form_url='', extra_context=None):
        "The 'Add new' admin view for this model."
        extra_context = extra_context or {}
        
        extra_context['dnaTypes'] = M.DnaComponentType.objects.all()
        extra_context['dnaCategories'] = M.DnaComponentType.objects.filter(subTypeOf=None)
        extra_context['cellTypes'] = M.CellComponentType.objects.all()
        extra_context['cellCategories'] = M.CellComponentType.objects.filter(subTypeOf=None)
        
        return super(ComponentAdmin, self).add_view(\
            request, form_url, extra_context=extra_context)

    def showDescription(self, obj):
        """
        @return: str; truncated description with full description mouse-over
        """
        if not obj.description: 
            return u''
        if len(obj.description) < 40:
            return unicode(obj.description)
        r = unicode(obj.description[:38])
        r = '<a title="%s">%s</a>' % (obj.description, F.truncate(obj.descriptionText(), 40))
        return r
    showDescription.allow_tags = True
    showDescription.short_description = 'Description'
    
    def showEdit(self, obj):
        """Small Edit Button for a direct link to Change dialog"""
        return safestring.mark_safe('<a href="%s"><img src="http://icons.iconarchive.com/icons/custom-icon-design/office/16/edit-icon.png"/></a>'\
                         % (obj.get_absolute_url_edit() ) )
    showEdit.allow_tags = True    
    showEdit.short_description = 'Edit'     

    def showStatus(self, obj):
        color = {u'available': '088A08', # green
                 u'planning': '808080', # grey
                 u'construction' : '0000FF', # blue
                 u'abandoned': 'B40404', # red
                 }
        return '<span style="color: #%s;">%s</span>' %\
               (color.get(obj.status, '000000'), obj.statusValue())
    showStatus.allow_tags = True
    showStatus.short_description = 'Status'
    
    def showType(self, obj):
        cat = unicode(obj.componentType.category())
        try:
            cat = cat[:4].replace(' ', '')
        except:
            pass
        return cat + '/ ' + unicode(obj.componentType.name)
    showType.allow_tags = True
    showType.short_description = 'Type'


class DnaComponentAdmin( BaseAdminMixin, reversion.VersionAdmin, ComponentAdmin):
    """Admin interface description for DNA constructs."""
    inlines = [ ComponentAttachmentInline ]
    form = forms.DnaComponentForm
    
    change_list_template = "admin/rotmic/dnacomponent/change_list.html"
    
    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentCategory', 'componentType'),
                       ('insert', 'vectorBackbone','markers' ),
                       )
        }
         ),
        ('Details', {
            'fields' : (('description',),
                        ('sequence', 'genbankFile'),
                        ),
        }
         ),            
    )

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy',
                    'showVectorUrl', 'showMarkerUrls', 
                    'showDescription', 'showType', 'showStatus', 'showEdit')
    
    list_filter = ( filters.DnaCategoryListFilter, filters.DnaTypeListFilter, 
                    'status', 
                    filters.MarkerTypeFilter, filters.MarkerListFilter,
                    filters.SortedUserFilter)
    
    search_fields = ('displayId', 'name', 'description', 
                     'insert__name', 'insert__displayId',
                     'vectorBackbone__name', 'vectorBackbone__displayId',
                     'vectorBackbone__markers__name', 'vectorBackbone__markers__displayId')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name')
    
    actions = ['make_csv']
    
    ## custom class variable for table generation
    csv_fields = OrderedDict( [('ID', 'displayId'),
                               ('Name', 'name'),
                               ('Status','status'),
                               ('Registered','registrationDate()'),
                               ('Author','registeredBy.username'),
                               ('Modified', 'modificationDate()'),
                               ('Modified By','modifiedBy.username'),
                               ('Category', 'componentType.category()'),
                               ('Type', 'componentType.name'),
                               ('Insert','insert.displayId'),
                               ('Vector','vectorBackbone.displayId'),
                               ('Markers',"markers.values_list('displayId', flat=True)"),
                               ('n Samples', 'allSamplesCount()'),
                               ('Description','description'),
                               ('Sequence','sequence')])
    
    
    def queryset(self, request):
        """Revert modification made by ComponentModelAdmin"""
        return super(ComponentAdmin,self).queryset(request)
 
        
    def get_form(self, request, obj=None, **kwargs):
        """
        Override queryset of ForeignKey fields without overriding the field itself.
        This preserves the "+" Button which is otherwise lost.
        See http://djangosnippets.org/snippets/1558/#c4674
        """
        form = super(DnaComponentAdmin,self).get_form(request, obj,**kwargs)

        ## suggest ID
        category = form.base_fields['componentCategory'].initial
        category = category.name[0].lower()
        prefix = request.user.profile.dcPrefix or request.user.profile.prefix
        prefix += category
        
        field = form.base_fields['displayId']
        field.initial = ids.suggestDnaId(request.user.id, prefix=prefix)
            
        return form

    def showInsertUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, M.DnaComponent), 'object missmatch'
        x = obj.insert
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>- %s' \
                              % (url, x.description, x.displayId, x.name))
    showInsertUrl.allow_tags = True
    showInsertUrl.short_description = 'Insert'
        
    def showVectorUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, M.DnaComponent), 'object missmatch'
        x = obj.vectorBackbone
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>- %s' \
                              % (url, x.description, x.displayId, x.name))
    showVectorUrl.allow_tags = True
    showVectorUrl.short_description = 'Base Vector'
    
    def showMarkerUrls(self, obj):
        """Table display of Vector Backbone markers"""
        assert isinstance(obj, M.DnaComponent), 'object missmatch'
        urls = []
        for m in obj.allMarkers():
            u = m.get_absolute_url()
            urls += [ html.mark_safe('<a href="%s" title="%s">%s</a>' \
                                % (u, m.description, m.name))]
        return ', '.join(urls)
    
    showMarkerUrls.allow_tags = True
    showMarkerUrls.short_description = 'Markers'

    def make_csv(self, request, queryset):
        return export_csv( request, queryset, self.csv_fields)
    make_csv.short_description = 'Export items as CSV'

admin.site.register(M.DnaComponent, DnaComponentAdmin)


class CellComponentAdmin( BaseAdminMixin, reversion.VersionAdmin, ComponentAdmin ):
    """Admin interface description for DNA constructs."""
    inlines = [ ComponentAttachmentInline ]
    form = forms.CellComponentForm
    
    change_list_template = "admin/rotmic/cellcomponent/change_list.html"

    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentCategory', 'componentType'),
                       ('plasmid', 'markers'),
                       )
        }
         ),
        ('Details', {
            'fields' : (('description',),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy',
                    'showPlasmidUrl', 'showMarkerUrls', 'showDescription',
                    'showType',
                    'showStatus', 'showEdit')
    
    list_filter = ( filters.CellCategoryListFilter, filters.CellTypeListFilter, 
                    'status', filters.SortedUserFilter)
    
    search_fields = ('displayId', 'name', 'description')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name',)
    
    actions = ['make_csv']
    
    ## custom class variable for table generation
    csv_fields = OrderedDict( [('ID', 'displayId'),
                               ('Name', 'name'),
                               ('Status','status'),
                               ('Registered','registrationDate()'),
                               ('Author','registeredBy.username'),
                               ('Modified', 'modificationDate()'),
                               ('Modified By','modifiedBy.username'),
                               ('Category', 'componentType.category()'),
                               ('Type', 'componentType.name'),
                               ('Plasmid','plasmid.displayId'),
                               ('Markers',"markers.values_list('displayId', flat=True)"),
                               ('n Samples', 'allSamplesCount()'),
                               ('Description','description')])

    def queryset(self, request):
        """Revert modification made by ComponentModelAdmin"""
        return super(ComponentAdmin,self).queryset(request)

    def get_form(self, request, obj=None, **kwargs):
        """
        Override queryset of ForeignKey fields without overriding the field itself.
        This preserves the "+" Button which is otherwise lost.
        See http://djangosnippets.org/snippets/1558/#c4674
        """
        form = super(CellComponentAdmin,self).get_form(request, obj,**kwargs)
        
        field = form.base_fields['markers']
        field.queryset = field.queryset.filter(componentType__subTypeOf=I.dcMarker)
        field.help_text = ''
        return form
    
    def showPlasmidUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, M.CellComponent), 'object missmatch'
        x = obj.plasmid
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>- %s' \
                              % (url, x.description, x.displayId, x.name))
    showPlasmidUrl.allow_tags = True
    showPlasmidUrl.short_description = 'Plasmid'
    
    def showMarkerUrls(self, obj):
        """Table display of Vector Backbone markers"""
        assert isinstance(obj, M.CellComponent), 'object missmatch'
        urls = []
        for m in obj.allMarkers():
            u = m.get_absolute_url()
            urls += [ html.mark_safe('<a href="%s" title="%s">%s</a>' \
                                % (u, m.description, m.name))]
        return ', '.join(urls)    
    showMarkerUrls.allow_tags = True
    showMarkerUrls.short_description = 'Markers'

    def make_csv(self, request, queryset):
        return export_csv( request, queryset, self.csv_fields)
    make_csv.short_description = 'Export items as CSV'


admin.site.register(M.CellComponent, CellComponentAdmin)


class OligoComponentAdmin( BaseAdminMixin, reversion.VersionAdmin, ComponentAdmin ):
    """Admin interface description for DNA constructs."""
    inlines = [ ComponentAttachmentInline ]
    form = forms.OligoComponentForm
    
    change_list_template = "admin/rotmic/oligocomponent/change_list.html"

    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentType',),
                       )
        }
         ),
        ('Details', {
            'fields' : (('sequence',),('purification', 'meltingTemp'), 
                        ('templates', 'reversePrimers'),('description',),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy',
                    'componentType', 'showTm', 'showDescription',
                    'showStatus','showEdit')
    
    list_filter = ( 'componentType', 'status', filters.SortedUserFilter)
    
    search_fields = ('displayId', 'name', 'description')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name',)
    
    actions = ['make_csv']
    
    ## custom class variable for table generation
    csv_fields = OrderedDict( [('ID', 'displayId'),
                               ('Name', 'name'),
                               ('Status','status'),
                               ('Registered','registrationDate()'),
                               ('Author','registeredBy.username'),
                               ('Modified', 'modificationDate()'),
                               ('Modified By','modifiedBy.username'),
                               ('Type', 'componentType.name'),
                               ('Tm', 'meltingTemp'),
                               ('Templates',"templates.values_list('displayId', flat=True)"),
                               ('n Samples', 'oligo_samples.count()'),
                               ('Description','description'),
                               ('Sequence','sequence')])

    def queryset(self, request):
        """Revert modification made by ComponentModelAdmin"""
        return super(ComponentAdmin,self).queryset(request)

    def showTm(self, obj):
        if obj.meltingTemp:
            return u'%02i\u00B0C' % obj.meltingTemp
        return ''
    showTm.allow_tags = True
    showTm.short_description = 'Tm'
    
    def make_csv(self, request, queryset):
        return export_csv( request, queryset, self.csv_fields)
    make_csv.short_description = 'Export items as CSV'

    
admin.site.register(M.OligoComponent, OligoComponentAdmin)


class ChemicalComponentAdmin( BaseAdminMixin, reversion.VersionAdmin, ComponentAdmin ):
    """Admin interface description for DNA constructs."""
    inlines = [ ComponentAttachmentInline ]
    form = forms.ChemicalComponentForm
    
    change_list_template = "admin/rotmic/chemicalcomponent/change_list.html"

    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentCategory', 'componentType'),
                       )
        }
         ),
        ('Details', {
            'fields' : (('cas','description',),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy',
                    'cas', 'showDescription', 'showType',
                    'showStatus',
                    'showEdit')
    
    list_filter = ( filters.ChemicalCategoryListFilter, filters.ChemicalTypeListFilter, 
                    'status', filters.SortedUserFilter)
    
    search_fields = ('displayId', 'name', 'description', 'cas')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name')
    
    actions = ['make_csv']

    ## custom class variable for table generation
    csv_fields = OrderedDict( [('ID', 'displayId'),
                               ('Name', 'name'),
                               ('Status','status'),
                               ('Registered','registrationDate()'),
                               ('Author','registeredBy.username'),
                               ('Modified', 'modificationDate()'),
                               ('Modified By','modifiedBy.username'),
                               ('Category', 'componentType.category()'),
                               ('Type', 'componentType.name'),
                               ('CAS', 'cas'),
                               ('n Samples', 'oligo_samples.count()'),
                               ('Description','description')])
    
    def queryset(self, request):
        """Revert modification made by ComponentModelAdmin"""
        return super(ComponentAdmin,self).queryset(request)

    def make_csv(self, request, queryset):
        return export_csv( request, queryset, self.csv_fields)
    make_csv.short_description = 'Export items as CSV'

admin.site.register(M.ChemicalComponent, ChemicalComponentAdmin)


