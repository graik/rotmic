from django.contrib import admin
import django.contrib.admin.widgets as widgets
import django.utils.html as html

import datetime

from rotmic.models import DnaComponent, DnaComponentType
from rotmic.utils.customadmin import ViewFirstModelAdmin
from rotmic.utils.adminFilters import DnaCategoryListFilter, DnaTypeListFilter
from rotmic.forms import DnaComponentForm
import rotmic.initialTypes as T


class BaseAdminMixin:
    """
    Automatically save and assign house-keeping information like by whom and
    when a record was saved.
    """

    def save_model(self, request, obj, form, change):
        """Override to save user who created this record"""
        if not change:
            obj.registeredBy = request.user
            obj.registeredAt = datetime.datetime.now()

        obj.save()

    def registrationDate(self, obj):
        """extract date from date+time"""
        return obj.registeredAt.date().isoformat()
    registrationDate.short_description = 'registered'
    
    def registrationTime(self, obj):
        """extract time from date+time"""
        return obj.registeredAt.time()
    registrationTime.short_description = 'at'
    

class DnaComponentAdmin( BaseAdminMixin, ViewFirstModelAdmin ):
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
##                        ('attachements',)
                        )
        }
         ),            
    )

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy',
                    'showInsertUrl', 'showVectorUrl', 'comment','status')
    
    list_filter = ( DnaCategoryListFilter, DnaTypeListFilter, 'status','registeredBy')
    
    search_fields = ('displayId', 'name', 'comment', 
                     'insert__name', 'insert__displayId',
                     'vectorBackbone__name', 'vectorBackbone__displayId')
    
##    list_editable = ('status',)
##    class Media:
##        js = ('jquery-2.0.1.min.js','jquery-ui.min.js')
    
        
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
        x = obj.insert
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s">%s</a>- %s' % (url, x.displayId, x.name))
    showInsertUrl.allow_tags = True
    showInsertUrl.short_description = 'Insert'
        
    def showVectorUrl(self, obj):
        """Table display of linked insert or ''"""
        x = obj.vectorBackbone
        if not x:
            return u''
        url = x.get_absolute_url()
        return html.mark_safe('<a href="%s">%s</a>- %s' % (url, x.displayId, x.name))
    showVectorUrl.allow_tags = True
    showVectorUrl.short_description = 'Vector'


class DnaComponentTypeAdmin( admin.ModelAdmin ):
    
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
                       

admin.site.register(DnaComponent, DnaComponentAdmin)
admin.site.register(DnaComponentType, DnaComponentTypeAdmin)
