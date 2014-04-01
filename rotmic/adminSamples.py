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
from django.http import HttpResponseRedirect

import reversion

import rotmic.models as M
import rotmic.templatetags.rotmicfilters as F
from . import forms

from .utils.customadmin import ViewFirstModelAdmin
from .utils import adminFilters as filters

from .adminBase import UserRecordMixin, RequestFormMixin, export_csv


class SampleAttachmentInline(admin.TabularInline):
    model = M.SampleAttachment
    form = forms.AttachmentForm

    ## Note: this template may be affected by:
    ## https://code.djangoproject.com/ticket/13696
    ## Todo: update to django 1.6 version of this template
    ## template = 'admin/rotmic/componentattachment/tabular.html'
    
    can_delete=True
    extra = 1
    max_num = 5

    fieldsets = (
        (None, {
            'fields': ('f', 'description',),
            'description': 'Only attach files that are specific to this very sample\n'\
                           +'Use DNA or Cell attachments otherwise.',
            
        }),
    )
    
class SampleProvenanceInline(admin.StackedInline):
    model = M.SampleProvenance
    fk_name = 'sample'  ## ensure provenance is attached to target sample (not to source sample)
    
    form = forms.SampleProvenanceForm
    
    can_delete=True
    extra = 1
    max_num = 5

    fieldsets = (
        (None, {
            'fields': (('provenanceType', 'sourceSample', 'description',),
                       ),
            'description': 'Specify how this sample was created or from which other sample it was derived from.',
        }),
    )

class SampleAdmin( UserRecordMixin, RequestFormMixin, reversion.VersionAdmin, ViewFirstModelAdmin ):
    form = forms.SampleForm     
    
    change_list_template = 'admin/rotmic/sample/change_list.html'  ## ReversionAdmin de-activated default template loading
    
    template = 'admin/rotmic/change_form_viewfirst.html'

    inlines = [ SampleProvenanceInline, SampleAttachmentInline ]
    date_hierarchy = 'preparedAt'
    
    fieldsets = [
        (None, {
            'fields' : ((('dummyfield',),('container', 'displayId', 'status'),
                         ('preparedAt', 'preparedBy', 'experimentNr'),
                         ('description'),
                    ))
            } ),
         ('Content', {
             'fields' : ((('concentration','concentrationUnit','amount','amountUnit',),
                         ('solvent','aliquotNr',),
                         )
                        ),
         }
        ), 
          
    ]
    list_display = ('showExtendedId', 'showRack', 'showLocation',
                    'showStatus',
                    'preparedAt', 'preparedBy', 'showType',
                    'showContent', 'showConcentration', 'showAmount',
                    'showEdit')
    
    ordering = ('container', 'displayId')

    save_as = True
    save_on_top = True

    search_fields = ['displayId', 
                     'preparedBy__username', 'preparedBy__first_name', 'preparedBy__last_name',
                     'description', 'experimentNr','solvent']
    
    list_filter = ('status', filters.SampleLocationFilter, 
                   filters.SampleRackFilter, filters.SampleContainerFilter,
                   filters.SortedPreparedByFilter)
    
    actions = ['make_csv']
    
    def __init__(self, *args, **kwargs):
        """Disable automatic link generation"""
        super(SampleAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = []
        
    def queryset(self, request):
        """
        Return actual sub-class instances instead of generic Sample super-class
        This method builds on the custom InheritanceManager replacing Sample.objects
        """
        return super(SampleAdmin,self).queryset(request).select_subclasses()
        
    def showRack(self, o):
        if not o.container.rack:
            return u''
        x = o.container.rack
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>' \
                              % (url, x.name, x.displayId) )
    showRack.allow_tags = True
    showRack.short_description = 'Rack'
        
    def showLocation(self, o):
        if not o.container.rack.location:
            return u''
        x = o.container.rack.location
        url = x.get_absolute_url()
        room = 'room %s' % x.room if x.room else ''
        temp = '%s C' % x.temperature if x.temperature else ''
        title = x.name
        title += ' (%s %s)' % (room, temp) if (room or temp) else ''
        return html.mark_safe('<a href="%s" title="%s">%s</a>' \
                              % (url, title, x.displayId) )
    showLocation.allow_tags = True
    showLocation.short_description = 'Location'

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
    
    def showStatus(self, obj):
        color = {u'ok': '088A08', # green
                 u'bad': 'B40404', # red
                 u'empty' : 'B40404', # red
                 u'preparing':  '0000FF', # blue
                 }
        return '<span style="color: #%s;">%s</span>' %\
               (color.get(obj.status, '000000'), obj.get_status_display())
    showStatus.allow_tags = True
    showStatus.short_description = 'Status'
        

    def showEdit(self, obj):
        return mark_safe('<a href="%s"><img src="http://icons.iconarchive.com/icons/custom-icon-design/office/16/edit-icon.png"/></a>'\
                         % (obj.get_absolute_url_edit() ) )
    showEdit.allow_tags = True    
    showEdit.short_description = 'Edit'     

    def make_csv(self, request, queryset):
        from collections import OrderedDict
        
        fields = OrderedDict( [('ID', 'displayId'),
                               ('Status','status'),
                               ('Container', 'container.displayId'),
                               ('Rack', 'container.rack.displayId'),
                               ('Location', 'container.rack.location.displayId'),
                               ('Registered','registrationDate()'),
                               ('Author','registeredBy.username'),
                               ('Modified', 'modificationDate()'),
                               ('Modified By','modifiedBy.username'),
                               ('Type', '_meta.verbose_name.split()[0]'),
                               ('Content_ID', 'content.displayId'),
                               ('Content_Name', 'content.name'),
                               ('Concentration', 'concentration'),
                               ('Conc.Unit', 'concentrationUnit'),
                               ('Amount', 'amount'),
                               ('Amount Unit', 'amountUnit'),
                               ('Solvent', 'solvent'),
                               ('ExperimentNr', 'experimentNr'),
                               ('Description','description')])
        return export_csv( request, queryset, fields)
    
    make_csv.short_description = 'Export samples as CSV'


admin.site.register( M.Sample, SampleAdmin )


class DnaSampleAdmin( SampleAdmin ):
    form = forms.DnaSampleForm
    
    change_list_template = 'admin/rotmic/dnasample/change_list.html'
    ## change_list_template = reversion.VersionAdmin.change_list_template ## revert change from SampleAdmin
    
    fieldsets = [
        (None, {
            'fields' : ((('dummyfield',),('container', 'displayId', 'status'),
                         ('preparedAt', 'preparedBy', 'experimentNr'),
                         ('description'),
                    ))
            } ),
         ('Content', {
             'fields' : ((('dna',),
                          ('concentration','concentrationUnit','amount','amountUnit',),
                          ('solvent','aliquotNr',),
                         )
                        ),
         }
        ), 
    ]

    list_display = ('showExtendedId', 'showRack', 'showLocation',
                    'showStatus',
                    'preparedAt', 'preparedBy',
                    'showContent', 'showConcentration', 'showAmount',
                    'showSequencing',
                    'showEdit')

    list_filter = ('status', filters.DnaSampleLocationFilter, 
                   filters.DnaSampleRackFilter, filters.DnaSampleContainerFilter,
                   'dna__projects', filters.SortedPreparedByFilter )
    
    actions = SampleAdmin.actions + ['make_sequencing']
    
    search_fields = SampleAdmin.search_fields + ['dna__displayId', 'dna__name']
        
    def queryset(self, request):
        """Revert modification made by SampleAdmin"""
        return super(SampleAdmin,self).queryset(request)

    def make_sequencing(self, request, queryset):
        """List view action to attach sequencing data to samples"""
        ## see https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/#actions-that-provide-intermediate-pages

        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        return HttpResponseRedirect("/rotmic/upload/tracefiles/?samples=%s" % (",".join(selected)))

    make_sequencing.short_description = 'Attach sequencing trace files'
    
admin.site.register( M.DnaSample, DnaSampleAdmin )


class CellSampleAdmin( SampleAdmin ):
    form = forms.CellSampleForm
    
    ##change_list_template = reversion.VersionAdmin.change_list_template ## revert change from SampleAdmin
    change_list_template = 'admin/rotmic/cellsample/change_list.html'
    
    
    fieldsets = [
        (None, {
            'fields' : ((('dummyfield',),('container', 'displayId', 'status'),
                         ('preparedAt', 'preparedBy', 'experimentNr'),
                         ('description'),
                    ))
            } ),
         ('Content', {
             'fields' : ((('cell',),
                          ('plasmid', 'cellCategory', 'cellType'),
                          ('amount','amountUnit',),
                          ('solvent','aliquotNr',),
                        )),
             'description': 'Select an <b>existing</b> Cell record <b>or</b> create a <b>new Cell</b> record on the fly from plasmid + strain below.'
         }
        ), 
    ]

    list_display = ('showExtendedId', 'showRack', 'showLocation',
                    'showStatus',
                    'preparedAt', 'preparedBy',
                    'showContent', 'showAmount',
                    'showEdit')
    
    list_filter = ('status', filters.CellSampleLocationFilter, 
                   filters.CellSampleRackFilter, filters.CellSampleContainerFilter,
                   'cell__projects', filters.SortedPreparedByFilter)

    search_fields = SampleAdmin.search_fields + \
        ['cell__displayId', 'cell__name', 'cell__plasmid__displayId', 'cell__plasmid__name']
        
    def queryset(self, request):
        """Revert modification made by SampleAdmin"""
        return super(SampleAdmin,self).queryset(request)
    
admin.site.register( M.CellSample, CellSampleAdmin )


class OligoSampleAdmin( SampleAdmin ):
    form = forms.OligoSampleForm
    
    ##change_list_template = reversion.VersionAdmin.change_list_template ## revert change from SampleAdmin
    change_list_template = 'admin/rotmic/oligosample/change_list.html'
    
    fieldsets = [
        (None, {
            'fields' : ((('dummyfield',),('container', 'displayId', 'status'),
                         ('preparedAt', 'preparedBy', 'experimentNr'),
                         ('description'),
                    ))
            } ),
         ('Content', {
             'fields' : ((('oligo',),
                          ('concentration','concentrationUnit','amount','amountUnit',),
                          ('solvent','aliquotNr',),
                         )
                        ),
         }
        ), 
    ]

    list_display = ('showExtendedId', 'showRack', 'showLocation',
                    'showStatus',
                    'preparedAt', 'preparedBy', 
                    'showContent', 'showConcentration', 'showAmount',
                    'showEdit')

    list_filter = ('status', filters.OligoSampleLocationFilter, 
                   filters.OligoSampleRackFilter, filters.OligoSampleContainerFilter,
                   'oligo__projects', filters.SortedPreparedByFilter)
        
    search_fields = SampleAdmin.search_fields + ['oligo__displayId', 'oligo__name']

    def queryset(self, request):
        """Revert modification made by SampleAdmin"""
        return super(SampleAdmin,self).queryset(request)
    
admin.site.register( M.OligoSample, OligoSampleAdmin )


class ChemicalSampleAdmin( SampleAdmin ):
    form = forms.ChemicalSampleForm
    
    ## change_list_template = reversion.VersionAdmin.change_list_template ## revert change from SampleAdmin
    change_list_template = 'admin/rotmic/chemicalsample/change_list.html'
    
    fieldsets = [
        (None, {
            'fields' : ((('dummyfield',),('container', 'displayId', 'status'),
                         ('preparedAt', 'preparedBy', 'experimentNr'),
                         ('description'),
                    ))
            } ),
         ('Content', {
             'fields' : ((('chemical',),
                          ('concentration','concentrationUnit','amount','amountUnit',),
                          ('solvent','aliquotNr',),
                         )
                        ),
         }
        ), 
    ]

    list_display = ('showExtendedId', 'showRack', 'showLocation',
                    'showStatus',
                    'preparedAt', 'preparedBy',
                    'showContent', 'showConcentration', 'showAmount',
                    'showEdit')

    list_filter = ('status', filters.ChemicalSampleLocationFilter, 
                   filters.ChemicalSampleRackFilter, filters.ChemicalSampleContainerFilter,
                   'chemical__projects', filters.SortedPreparedByFilter)
        
    search_fields = SampleAdmin.search_fields + ['chemical__displayId', 'chemical__name']

    def queryset(self, request):
        """Revert modification made by SampleAdmin"""
        return super(SampleAdmin,self).queryset(request)
    
admin.site.register( M.ChemicalSample, ChemicalSampleAdmin )


class ProteinSampleAdmin( SampleAdmin ):
    form = forms.ProteinSampleForm
    
    ## change_list_template = reversion.VersionAdmin.change_list_template ## revert change from SampleAdmin
    change_list_template = 'admin/rotmic/proteinsample/change_list.html'
    
    fieldsets = [
        (None, {
            'fields' : ((('dummyfield',),('container', 'displayId', 'status'),
                         ('preparedAt', 'preparedBy', 'experimentNr'),
                         ('description'),
                    ))
            } ),
         ('Content', {
             'fields' : ((('protein',),
                          ('concentration','concentrationUnit','amount','amountUnit',),
                          ('solvent','aliquotNr',),
                         )
                        ),
         }
        ), 
    ]

    list_display = ('showExtendedId', 'showRack', 'showLocation',
                    'showStatus',
                    'preparedAt', 'preparedBy',
                    'showContent', 'showConcentration', 'showAmount',
                    'showEdit')

    list_filter = ('status', filters.ProteinSampleLocationFilter, 
                   filters.ProteinSampleRackFilter, filters.ProteinSampleContainerFilter,
                   'protein__projects', filters.SortedPreparedByFilter)
        
    search_fields = SampleAdmin.search_fields + ['protein__displayId', 'protein__name']

    def queryset(self, request):
        """Revert modification made by SampleAdmin"""
        return super(SampleAdmin,self).queryset(request)
    
admin.site.register( M.ProteinSample, ProteinSampleAdmin )


