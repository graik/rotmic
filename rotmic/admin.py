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

from django.contrib import admin
import django.contrib.admin.widgets as widgets
import django.utils.html as html
from django.utils.safestring import mark_safe

import reversion

import datetime

from rotmic.models import DnaComponent, DnaComponentType, ComponentAttachment, \
     CellComponent, CellComponentType, Unit, Sample, SampleAttachment, \
     Location, Rack, Container, DnaSample

from rotmic.utils.customadmin import ViewFirstModelAdmin, ComponentModelAdmin

import rotmic.utils.adminFilters as filters

from rotmic.forms import DnaComponentForm, CellComponentForm, AttachmentForm,\
     SampleForm, LocationForm, RackForm, ContainerForm, DnaSampleForm

import rotmic.initialTypes as T
import rotmic.templatetags.rotmicfilters as F


class BaseAdminMixin:
    """
    Automatically save and assign house-keeping information like by whom and
    when a record was saved.
    """

    def save_model(self, request, obj, form, change):
        """Override to save user who created this record"""
        ## do if new object or if object is being recovered by reversion
        if not change or '/recover/' in request.META['HTTP_REFERER']:
            obj.registeredBy = request.user
            obj.registeredAt = datetime.datetime.now()
            
        if change and form.has_changed():
            obj.modifiedBy = request.user
            obj.modifiedAt = datetime.datetime.now()

        obj.save()


class ComponentAttachmentInline(admin.TabularInline):
    model = ComponentAttachment
    form = AttachmentForm
    template = 'admin/rotmic/componentattachment/tabular.html'
    can_delete=True
    extra = 1
    max_num = 5


class DnaComponentAdmin( BaseAdminMixin, reversion.VersionAdmin, ComponentModelAdmin ):
    """Admin interface description for DNA constructs."""
    inlines = [ ComponentAttachmentInline ]
    form = DnaComponentForm
    
    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentCategory', 'componentType'),
                       ('insert', 'vectorBackbone','marker' ),
                       )
        }
         ),
        ('Details', {
            'fields' : (('comment',),
                        ('sequence', 'genbankFile'),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy',
                    'showInsertUrl', 'showVectorUrl', 'showMarkerUrls', 
                    'showComment','showStatus', 'showEdit')
    
    list_filter = ( filters.DnaCategoryListFilter, filters.DnaTypeListFilter, 'status','registeredBy')
    
    search_fields = ('displayId', 'name', 'comment', 
                     'insert__name', 'insert__displayId',
                     'vectorBackbone__name', 'vectorBackbone__displayId')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name',)
    
 
    def save_model(self, request, obj, form, change):
        """Extract uploaded genbank file from request"""
        if request.FILES and 'genbankFile' in request.FILES:
            obj.genbank = ''.join(request.FILES['genbankFile'].readlines())
        super(DnaComponentAdmin, self).save_model( request, obj, form, change)
 
        
    def get_form(self, request, obj=None, **kwargs):
        """
        Override queryset of ForeignKey fields without overriding the field itself.
        This preserves the "+" Button which is otherwise lost.
        See http://djangosnippets.org/snippets/1558/#c4674
        """
        form = super(DnaComponentAdmin,self).get_form(request, obj,**kwargs)

        field = form.base_fields['marker']
        field.queryset = field.queryset.filter(componentType__subTypeOf=T.dcMarker)
        field.help_text = 'select multiple with Control/Command key'
        
        field = form.base_fields['vectorBackbone']
        field.empty_label = '---specifiy vector---'
            
        return form

    def showInsertUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, DnaComponent), 'object missmatch'
        x = obj.insert
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>- %s' \
                              % (url, x.comment, x.displayId, x.name))
    showInsertUrl.allow_tags = True
    showInsertUrl.short_description = 'Insert'
        
    def showVectorUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, DnaComponent), 'object missmatch'
        x = obj.vectorBackbone
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>- %s' \
                              % (url, x.comment, x.displayId, x.name))
    showVectorUrl.allow_tags = True
    showVectorUrl.short_description = 'Vector'
    
    def showMarkerUrls(self, obj):
        """Table display of Vector Backbone markers"""
        assert isinstance(obj, DnaComponent), 'object missmatch'
        urls = []
        for m in obj.allMarkers():
            u = m.get_absolute_url()
            urls += [ html.mark_safe('<a href="%s" title="%s">%s</a>' \
                                % (u, m.comment, m.name))]
        return ', '.join(urls)
    
    showMarkerUrls.allow_tags = True
    showMarkerUrls.short_description = 'Markers'

admin.site.register(DnaComponent, DnaComponentAdmin)


class CellComponentAdmin( BaseAdminMixin, reversion.VersionAdmin, ComponentModelAdmin ):
    """Admin interface description for DNA constructs."""
    inlines = [ ComponentAttachmentInline ]
    form = CellComponentForm
    
    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentCategory', 'componentType'),
                       ('plasmid', 'marker'),
                       )
        }
         ),
        ('Details', {
            'fields' : (('comment',),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy',
                    'showPlasmidUrl', 'showMarkerUrls', 'showComment','showStatus',
                    'showEdit')
    
    list_filter = ( filters.CellCategoryListFilter, filters.CellTypeListFilter, 
                    'status','registeredBy')
    
    search_fields = ('displayId', 'name', 'comment')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name',)
    

    def get_form(self, request, obj=None, **kwargs):
        """
        Override queryset of ForeignKey fields without overriding the field itself.
        This preserves the "+" Button which is otherwise lost.
        See http://djangosnippets.org/snippets/1558/#c4674
        """
        form = super(CellComponentAdmin,self).get_form(request, obj,**kwargs)
        
        field = form.base_fields['marker']
        field.queryset = field.queryset.filter(componentType__subTypeOf=T.dcMarker)
        field.help_text = ''
        return form
    
    def showPlasmidUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, CellComponent), 'object missmatch'
        x = obj.plasmid
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="%s">%s</a>- %s' \
                              % (url, x.comment, x.displayId, x.name))
    showPlasmidUrl.allow_tags = True
    showPlasmidUrl.short_description = 'Plasmid'
    
    def showMarkerUrls(self, obj):
        """Table display of Vector Backbone markers"""
        assert isinstance(obj, CellComponent), 'object missmatch'
        urls = []
        for m in obj.allMarkers():
            u = m.get_absolute_url()
            urls += [ html.mark_safe('<a href="%s" title="%s">%s</a>' \
                                % (u, m.comment, m.name))]
        return ', '.join(urls)    
    showMarkerUrls.allow_tags = True
    showMarkerUrls.short_description = 'Markers'

admin.site.register(CellComponent, CellComponentAdmin)


class DnaComponentTypeAdmin( reversion.VersionAdmin, admin.ModelAdmin ):
    
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
                       

admin.site.register(DnaComponentType, DnaComponentTypeAdmin)


class CellComponentTypeAdmin( reversion.VersionAdmin, admin.ModelAdmin ):
    
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

admin.site.register(CellComponentType, CellComponentTypeAdmin)
    

class UnitAdmin( admin.ModelAdmin ):
    
    fieldsets = (
        (None, {
            'fields': (('name', 'unitType',),
                       ('conversion',),
                       )
            }
         ),
        )
    
    list_display = ('name','unitType', 'conversion')
    list_filter = ('unitType',)
    
admin.site.register( Unit, UnitAdmin )


class SampleAttachmentInline(admin.TabularInline):
    model = SampleAttachment
    form = AttachmentForm
    template = 'admin/rotmic/componentattachment/tabular.html'
    can_delete=True
    extra = 1
    max_num = 5

    fieldsets = (
        (None, {
            'fields': ('f', 'description',),
            'description': 'Only attach files that are specific to this very sample\n'\
                           +'Use DNA or Cell attachments otherwise.',
            'classes': ('collapse',),
            
        }),
    )
    

class SampleAdmin( BaseAdminMixin, reversion.VersionAdmin, ViewFirstModelAdmin ):
    form = SampleForm     
    
    change_list_template = 'admin/rotmic/sample/change_list.html'  ## for some reason this is needed.

    inlines = [ SampleAttachmentInline ]
    date_hierarchy = 'preparedAt'
    
    fieldsets = [
        (None, {
            'fields' : ((('container', 'displayId', 'status'),
                         ('preparedAt',),
                         ('comment'),
                    ))
            } ),
         ('Content', {
             'fields' : ((('concentration','concentrationUnit','amount','amountUnit',),
                         ('solvent','aliquotNr',),
                         )
                        )
        }
        ), 
          
    ]
    list_display = ('showExtendedId', 'showRack', 'showLocation',
                    'preparedAt', 'registeredBy',
                    'showContent', 'showConcentration', 'showAmount',
                    'showStatus','showEdit')
    
    ordering = ('container', 'displayId')

    save_as = True
    save_on_top = True

    search_fields = ('diplayId', 'name','comment')
    
    list_filter = ('status', filters.SampleLocationFilter, 
                   filters.SampleRackFilter, filters.SampleContainerFilter)
    
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

    def showConcentration(self, o):
        conc = unicode(o.concentration or '')
        unit = unicode(o.concentrationUnit or '')
        return conc + ' '+ unit
    showConcentration.short_description = 'Concentration' 
    
    def showAmount(self, o):
        amount = unicode( o.amount or '' )
        unit   = unicode( o.amountUnit or '' )
        return amount + ' '+ unit
    showAmount.short_description = 'Amount' 
    
    def showComment(self, obj):
        """
        @return: str; truncated comment with full comment mouse-over
        """
        if not obj.comment: 
            return u''
        if len(obj.comment) < 40:
            return unicode(obj.comment)
        r = unicode(obj.comment[:38])
        r = '<a title="%s">%s</a>' % (obj.comment, F.truncate(obj.commentText(), 40))
        return r
    showComment.allow_tags = True
    showComment.short_description = 'Description'
    
    def showStatus(self, obj):
        color = {u'ok': '088A08', # green
                 u'bad': 'B40404', # red
                 u'empty' : 'B40404', # red
                 u'preparing':  '0000FF', # blue
                 }
        return '<span style="color: #%s;">%s</span>' %\
               (color.get(obj.status, '000000'), obj.status)
    showStatus.allow_tags = True
    showStatus.short_description = 'Status'
        

    def showEdit(self, obj):
        return mark_safe('<a href="%s"><img src="http://icons.iconarchive.com/icons/custom-icon-design/office/16/edit-icon.png"/></a>'\
                         % (obj.get_absolute_url_edit() ) )
    showEdit.allow_tags = True    
    showEdit.short_description = 'Edit'     

admin.site.register( Sample, SampleAdmin )


class DnaSampleAdmin( SampleAdmin ):
    form = DnaSampleForm
    change_list_template = reversion.VersionAdmin.change_list_template ## revert change from SampleAdmin
    
    fieldsets = [
        (None, {
            'fields' : ((('container', 'displayId', 'status'),
                         ('preparedAt',),
                         ('comment'),
                    ))
            } ),
         ('Content', {
             'fields' : ((('dna',),
                          ('concentration','concentrationUnit','amount','amountUnit',),
                          ('solvent','aliquotNr',),
                         )
                        )
        }
        ), 
    ]

    list_filter = ('status', filters.DnaSampleLocationFilter, 
                   filters.DnaSampleRackFilter, filters.DnaSampleContainerFilter,
                   'registeredBy')
        
    def queryset(self, request):
        """Revert modification made by SampleAdmin"""
        return super(SampleAdmin,self).queryset(request)
    
admin.site.register( DnaSample, DnaSampleAdmin )



class LocationAdmin(BaseAdminMixin, reversion.VersionAdmin, ViewFirstModelAdmin):
    form = LocationForm

    fieldsets = [
        (None, {
            'fields' : ((('displayId', 'name'),
                         ('temperature','room'),
                        )),
            'description' : 'Describe a freezer, row of shelves or similar storage location.'
            }
         )
        ]

    list_display = ('displayId', 'name', 'temperature', 'room')
    list_filter = ('room', 'temperature')
    search_fields = ('displayId', 'name',)

    save_as = True

admin.site.register( Location, LocationAdmin )

class RackAdmin(BaseAdminMixin, reversion.VersionAdmin, ViewFirstModelAdmin):
    form = RackForm

    fieldsets = [
        (None, {
            'fields' : ((('location', 'displayId', 'name'),
                        )),
            'description' : 'Describe a freezer rack, single shelve or similar holder of containers.'
            }
         )
        ]

    list_display = ('displayId', 'location', 'name',)
    list_filter = ('location',)
    search_fields = ('displayId', 'name',)

    save_as = True

admin.site.register( Rack, RackAdmin )


class ContainerAdmin(BaseAdminMixin, reversion.VersionAdmin):
    form = ContainerForm

    fieldsets = [
        (None, {
            'fields' : ((('rack', 'displayId', 'name'),
                         ('containerType',),
                         ('comment',),
                        )),
            'description' : 'Describe a sample container or box.'
            }
         )
        ]

    list_display = ('__unicode__', 'showRackUrl', 'showLocationUrl', 'containerType')
    list_filter =  ('containerType', 'rack__location', filters.RackListFilter)
    search_fields = ('displayId', 'name','comment')

    save_as = True

    def showLocationUrl(self, obj):
        """Table display of linked insert or ''"""
        assert isinstance(obj, Container), 'object missmatch'
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
        assert isinstance(obj, Container), 'object missmatch'
        x = obj.rack
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s" title="">%s</a>' \
                              % (url, unicode(x)) )
    showRackUrl.allow_tags = True
    showRackUrl.short_description = 'Rack'

admin.site.register( Container, ContainerAdmin )

