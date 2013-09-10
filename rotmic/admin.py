from django.contrib import admin
import django.contrib.admin.widgets as widgets
import django.utils.html as html

import reversion

import datetime

from rotmic.models import DnaComponent, DnaComponentType, ComponentAttachment
from rotmic.utils.customadmin import ViewFirstModelAdmin
from rotmic.utils.adminFilters import DnaCategoryListFilter, DnaTypeListFilter
from rotmic.forms import DnaComponentForm
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


class AttachmentInline(admin.TabularInline):
    model = ComponentAttachment
    extra = 1
    max_num = 5

class ComponentVersionAdapter(reversion.VersionAdapter):
    exclude = ('componentCategory',)
    ## doesn't work yet

## ToDo: create custom VersionAdmin which uses a different revision_manager
## create custom RevisionManager where register() is using a custom VersionAdapter
## create custom VersionAdapter where exclude is set to exclude 'componentCategory'
class DnaComponentAdmin( BaseAdminMixin, reversion.VersionAdmin, ViewFirstModelAdmin ):
    inlines = [ AttachmentInline ]
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
                        ('sequence'),
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy',
                    'showInsertUrl', 'showVectorUrl', 'showMarkerUrls', 'showComment','status')
    
    list_filter = ( DnaCategoryListFilter, DnaTypeListFilter, 'status','registeredBy')
    
    search_fields = ('displayId', 'name', 'comment', 
                     'insert__name', 'insert__displayId',
                     'vectorBackbone__name', 'vectorBackbone__displayId')
    
    date_hierarchy = 'registeredAt'
    
    ordering = ('displayId', 'name',)
    
        
    def _autoregister(self, model, follow=None):
        """Registers a model with reversion, if required."""
        if model._meta.proxy:
            raise RegistrationError("Proxy models cannot be used with django-reversion, register the parent class instead")
        if not self.revision_manager.is_registered(model):
            follow = follow or []
            for parent_cls, field in model._meta.parents.items():
                follow.append(field.name)
                self._autoregister(parent_cls)
            self.revision_manager.register(model, adapter_cls=ComponentVersionAdapter, 
                                           follow=follow, format=self.reversion_format)


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
        category = obj.componentType.category()
        v = obj if category == T.dcVectorBB else obj.vectorBackbone
        r = u''
        if v:
            markers = [ m.name for m in v.marker.all() ]
            r += ', '.join(markers)
        return r
    showMarkerUrls.allow_tags = True
    showMarkerUrls.short_description = 'Markers'
    
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
    

admin.site.register(DnaComponent, DnaComponentAdmin)


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
