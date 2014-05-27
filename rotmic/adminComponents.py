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
"""Admin interface for Component and derrived classes"""

import StringIO
from collections import OrderedDict

from django.contrib import admin, messages
from django.utils import safestring, html
import django.contrib.staticfiles.templatetags.staticfiles as ST
from django.http import HttpResponseRedirect

import reversion
from Bio import SeqIO

from . import models as M
from . import forms
from . import initialTypes as I
from .templatetags import rotmicfilters as F
from .utils import adminFilters as filters
from .utils import ids
from .utils.customadmin import ViewFirstModelAdmin

from .adminBase import UserRecordMixin, RequestFormMixin, export_csv, UpdateManyMixin


class ComponentAttachmentInline(admin.TabularInline):
    model = M.ComponentAttachment
    form = forms.AttachmentForm
    can_delete=True
    extra = 1
    max_num = 5

class ComponentAdmin( UserRecordMixin, RequestFormMixin, ViewFirstModelAdmin, UpdateManyMixin ):
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
    * showStatus
    * showFirstAuthor -- show first; indicate by '+' if there is additional authors
    * showSampleStatus -- pretty symbols for availability of samples
    * showType -- shortened text repr. of category/Type
    """
    
    permit_delete = ['registeredBy', 'authors']
    
    ## custom class variable for table generation
    csv_fields = OrderedDict( [('ID', 'displayId'),
                               ('Name', 'name'),
                               ('Status','status'),
                               ('Registered','registrationDate()'),
                               ('By','registeredBy.username'),
                               ('Authors', "authors.values_list('username', flat=True)"),
                               ('Modified', 'modificationDate()'),
                               ('Modified By','modifiedBy.username'),
                               ('Projects', "projects.values_list('name', flat=True)"),
                               ('Category', 'componentType.category()'),
                               ('Type', 'componentType.name'),
                               ])

    actions = ['make_update',
               'delete_selected',  ## This is needed to activate non-author delete protection               
               ]  
    
    ## list field names that should be excluded from the bulk update dialog
    exclude_from_update = ['displayId', 'name', 'category', 'componentCategory']
    
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
    
    def showType(self, obj):
        cat = unicode(obj.componentType.category())
        try:
            cat = cat[0].upper()
        except:
            pass
        return cat + '/ ' + unicode(obj.componentType.name)
    showType.allow_tags = True
    showType.short_description = 'Type'

    def showFirstAuthor(self, obj):
        r = u'%s' % obj.authors.first()
        if obj.authors.count() > 1:
            r += '+'
        return r
    showFirstAuthor.allow_tags = True
    showFirstAuthor.short_description = 'Authors'

    def showSampleStatus(self, obj):
        fyes = ST.static('admin/img/icon-yes.gif')

        n = obj.samples.count()
        x = 's' if n > 1 else ''

        r1 = '<img src="%s" title="%i sample%s">' % (fyes, n, x)
        r1 = r1 if n else '<span title="no samples">&mdash;</span>'
        
        return html.mark_safe(r1)

    showSampleStatus.allow_tags = True    
    showSampleStatus.short_description = '' 


class DnaComponentAdmin( reversion.VersionAdmin, ComponentAdmin):
    """Admin interface description for DNA constructs."""
    inlines = [ ComponentAttachmentInline ]
    form = forms.DnaComponentForm
    
    change_list_template = "admin/rotmic/dnacomponent/change_list.html"
    
    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentCategory', 'componentType'),
                       ('insert', 'vectorBackbone','markers', 'translatesTo' ),
                       )
        }
         ),
        ('Details', {
            'fields' : (
                        ('authors', 'projects'), ('description',),
                        ('genbankFile', 'genbankClear', 'sequence',),
                        ),
        }
         ),            
    )

    list_display = ('displayId', #2
                    'name', #2
                    'showStatus', #3
                    'showComments', #4
                    'registrationDate', #4
                    'showFirstAuthor', #5
                    'showVectorUrl', 'showMarkerUrls', #9 ## Time sink!!
                    'showDescription', #9
                    'showType', #9
                    'showSampleStatus', #12 Time sink!!
                    'showEdit' #13
                   )
    
    list_filter = ( filters.DnaCategoryListFilter, filters.DnaTypeListFilter, 
                    'status', 
                    filters.MarkerTypeFilter, filters.MarkerListFilter,
                    'projects', filters.SortedAuthorFilter)
    
    search_fields = ('displayId', 'name', 'description', 
                     'insert__name', 'insert__displayId',
                     'vectorBackbone__name', 'vectorBackbone__displayId',
                     'vectorBackbone__markers__name', 'vectorBackbone__markers__displayId',
                     'projects__name')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name')
    
    actions = ComponentAdmin.actions + ['make_csv', 'make_genbank']
    
    ## custom class variable for table generation
    csv_fields = OrderedDict( ComponentAdmin.csv_fields.items() + 
                              [
                               ('Insert', 'insert.displayId'),
                               ('Vector', 'vectorBackbone.displayId'),
                               ('Markers', "markers.values_list('displayId', flat=True)"),
                               ('n Samples', 'allSamplesCount()'),
                               ('Description','description'),
                               ('Sequence','sequence') 
                              ] )
    
    exclude_from_update = ComponentAdmin.exclude_from_update +\
        ['genbankFile', 'genbankClear', 'sequence']
    
    SMPL_ICON = ST.static('admin/img/icon-yes.gif')
    
    def queryset(self, request):
        """Revert modification made by ComponentModelAdmin"""
        return super(ComponentAdmin,self).queryset(request)
 
        
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
        """Table display of linked vector or ''"""
        assert isinstance(obj, M.DnaComponent), 'object missmatch'
        x = obj.vectorBackbone
        if not x:
            return u''
        url = x.get_absolute_url()
        name = x.name or x.displayId
        description = '%s (%s)\n%s' % (x.displayId, x.name, x.description)
        return html.mark_safe('<a href="%s" title="%s">%s</a>' \
                              % (url, description, name))
    showVectorUrl.allow_tags = True
    showVectorUrl.short_description = 'Base Vector'
    
    ## profiles to 0.030 s  * 100 for a full table; culprite is allMarkers
    ##@profilehooks.profile(filename='/tmp/djangoprofile.out', immediate=True)
    def showMarkerUrls(self, obj):
        """Table display of Vector Backbone markers"""
        assert isinstance(obj, M.DnaComponent), 'object missmatch'
        urls = []
        
        for m in obj.allMarkers():
            u = m.get_absolute_url()
            urls += [ '<a href="%s" title="%s">%s</a>' \
                                % (u, m.description, m.name)]
        return html.mark_safe(', '.join(urls))
    
    showMarkerUrls.allow_tags = True
    showMarkerUrls.short_description = 'Markers'

    def showSampleStatus(self, obj):
        n_dna = obj.samples.count()
        n_cells = obj.cellSamples.count()

        ## don't show icons for non-plasmid constructs unless there are
        ## samples registered.
        if obj.componentType.category() != I.dcPlasmid:
            if not (n_dna or n_cells):
                return ''

        fyes = self.SMPL_ICON
            
        x_dna = 's' if n_dna > 1 else ''
        x_cells = 's' if n_cells > 1 else ''

        r1 = '<img src="%s" title="%i DNA sample%s">' % (fyes, n_dna, x_dna)
        r2 = '<img src="%s" title="%i Cell sample%s">'% (fyes, n_cells, x_cells)

        r1 = r1 if n_dna else '<span title="no DNA samples">&mdash;</span>'
        r2 = r2 if n_cells else '<span title="no cell samples">&mdash;</span>'
        
        return html.mark_safe('%s / %s' % (r1, r2))

    showSampleStatus.allow_tags = True    
    showSampleStatus.short_description = 'Smpls' 


    def make_csv(self, request, queryset):
        return export_csv( request, queryset, self.csv_fields)
    make_csv.short_description = 'Export items as CSV'

    def make_genbank(self, request, queryset):
        """List view action to attach sequencing data to samples"""
        ## see https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages

        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/rotmic/upload/genbank/?constructs=%s" % (",".join(selected)))

    make_genbank.short_description = 'Attach genbank records'

admin.site.register(M.DnaComponent, DnaComponentAdmin)


class CellComponentAdmin( reversion.VersionAdmin, ComponentAdmin ):
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
            'fields' : (('authors', 'projects'), ('description',),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'showStatus', 'showComments',
                    'registrationDate', 'showFirstAuthor',
                    'showPlasmidUrl', 'showMarkerUrls', 'showDescription',
                    'showType',
                    'showSampleStatus', 'showEdit')
    
    list_filter = ( filters.CellCategoryListFilter, filters.CellTypeListFilter, 
                    'status', 'projects', filters.SortedAuthorFilter)
    
    search_fields = ('displayId', 'name', 'description', 'projects__name')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name',)
    
    actions = ['make_csv'] + ComponentAdmin.actions
    
    ## custom class variable for table generation
    csv_fields = OrderedDict( ComponentAdmin.csv_fields.items() + 
                              [
                               ('Plasmid','plasmid.displayId'),
                               ('Markers',"markers.values_list('displayId', flat=True)"),
                               ('n Samples', 'allSamplesCount()'),
                               ('Description','description')
                              ])

    def queryset(self, request):
        """Revert modification made by ComponentModelAdmin"""
        return super(ComponentAdmin,self).queryset(request)

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


class OligoComponentAdmin( reversion.VersionAdmin, ComponentAdmin ):
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
            'fields' : (('authors', 'projects'), 
                        ('sequence',),('purification', 'meltingTemp'), 
                        ('templates', 'reversePrimers'),
                        ('description',),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'showStatus', 'showComments',
                    'registrationDate', 'showFirstAuthor',
                    'showTm', 'showDescription',
                    'componentType',
                    'showSampleStatus', 'showEdit')
    
    list_filter = ( 'componentType', 'status', 'projects', filters.SortedAuthorFilter)
    
    search_fields = ('displayId', 'name', 'description', 'projects__name')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name',)
    
    actions = ['make_csv'] + ComponentAdmin.actions

    ## custom class variable for table generation
    csv_fields = OrderedDict( [('ID', 'displayId'),
                               ('Name', 'name'),
                               ('Status','status'),
                               ('Registered','registrationDate()'),
                               ('Author','registeredBy.username'),
                               ('Modified', 'modificationDate()'),
                               ('Modified By','modifiedBy.username'),
                               ('Projects', "projects.values_list('name', flat=True)"),
                               ('Type', 'componentType.name'),
                               ('Tm', 'meltingTemp'),
                               ('Templates',"templates.values_list('displayId', flat=True)"),
                               ('n Samples', 'oligo_samples.count()'),
                               ('Description','description'),
                               ('Sequence','sequence')])

    exclude_from_update = ComponentAdmin.exclude_from_update + ['sequence']

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


class ChemicalComponentAdmin( reversion.VersionAdmin, ComponentAdmin ):
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
            'fields' : (('authors','projects'), 
                        ('cas','description'),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'showStatus', 'showComments',
                    'registrationDate', 'showFirstAuthor',
                    'cas', 'showDescription', 
                    'showType',
                    'showSampleStatus', 'showEdit')
    
    list_filter = ( filters.ChemicalCategoryListFilter, filters.ChemicalTypeListFilter, 
                    'status', 'projects', filters.SortedAuthorFilter)
    
    search_fields = ('displayId', 'name', 'description', 'cas', 'projects__name')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name')
    
    actions = ['make_csv'] + ComponentAdmin.actions

    ## custom class variable for table generation
    csv_fields = OrderedDict( ComponentAdmin.csv_fields.items() + 
                              [
                               ('CAS', 'cas'),
                               ('n Samples', 'chemical_samples.count()'),
                               ('Description','description')
                              ])
    
    def queryset(self, request):
        """Revert modification made by ComponentModelAdmin"""
        return super(ComponentAdmin,self).queryset(request)

    def make_csv(self, request, queryset):
        return export_csv( request, queryset, self.csv_fields)
    make_csv.short_description = 'Export items as CSV'

admin.site.register(M.ChemicalComponent, ChemicalComponentAdmin)


class ProteinComponentAdmin( reversion.VersionAdmin, ComponentAdmin ):
    """Admin interface description for DNA constructs."""
    inlines = [ ComponentAttachmentInline ]
    form = forms.ProteinComponentForm
    
    change_list_template = "admin/rotmic/proteincomponent/change_list.html"

    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentCategory', 'componentType'),
                       )
        }
         ),
        ('Details', {
            'fields' : (('authors', 'projects'), ('description',),
                        ('sequence', 'genbankFile', 'genbankClear', 'encodedBy'),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'showStatus', 'showComments',
                    'registrationDate', 'showFirstAuthor',
                    'showDescription','showSampleStatus','showEdit')
    
    list_filter = ( filters.ProteinCategoryListFilter, filters.ProteinTypeListFilter, 
                    'status', 'projects', filters.SortedAuthorFilter)
    
    search_fields = ('displayId', 'name', 'description','projects__name')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name')
    
    actions = ['make_csv', 'make_genbank'] + ComponentAdmin.actions

    ## custom class variable for table generation
    csv_fields = OrderedDict( ComponentAdmin.csv_fields.items() + 
                              [
                               ('n Samples', 'protein_samples.count()'),
                               ('Description','description'),
                               ('Sequence', 'sequence'),                               
                              ])
 
    exclude_from_update = ComponentAdmin.exclude_from_update +\
        ['sequence', 'genbankFile', 'genbankClear', 'encodedBy']
    
    def queryset(self, request):
        """Revert modification made by ComponentModelAdmin"""
        return super(ComponentAdmin,self).queryset(request)

    def make_csv(self, request, queryset):
        return export_csv( request, queryset, self.csv_fields)
    make_csv.short_description = 'Export items as CSV'
    
    def make_genbank(self, request, queryset):
        """List view action to attach sequencing data to samples"""
        ## see https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages

        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/rotmic/upload/genbankaa/?constructs=%s" % (",".join(selected)))

    make_genbank.short_description = 'Attach genbank records'

    def save_model(self, request, obj, form, change):
        """
        Save DnaComponent.translatesTo relation to new Protein instance if
        given via URL like add/?encodedBy=1
        This cannot be done on the ModelForm.save level because the latter is called
        with commit=False.
        """
        super(ProteinComponentAdmin, self).save_model(request, obj, form, change)
        
        encodedBy = form.cleaned_data.get('encodedBy', None)
        if encodedBy:
            try:
                encodedBy.translatesTo = form.instance
                encodedBy.save()
                msg = 'Updated DNA construct %s.' % str(encodedBy)
                messages.success(request, msg)
            except Exception, why:
                msg = 'Could not create translatesTo relation with %r. Reason: %s'\
                    % (encodedBy, why)
                messages.error(request, msg)
        

admin.site.register(M.ProteinComponent, ProteinComponentAdmin)

