from django.contrib import admin

import datetime

from rotmic.models import DnaComponent, DnaComponentType
from rotmic.utils.customadmin import ViewFirstModelAdmin
from rotmic.forms import DnaComponentForm


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
                    'insert','vectorBackbone', 'comment','status')

    def get_form(self, request, obj=None, **kwargs):
        """
        Override queryset of ForeignKey fields without overriding the field itself.
        This preserves the "+" Button which is otherwise lost.
        See http://djangosnippets.org/snippets/1558/#c4674
        """
        typeMarker = DnaComponentType.objects.get(name='Marker')
        typeInsert = DnaComponentType.objects.get(name='Insert')
        typeVectorBB = DnaComponentType.objects.get(name='Vector Backbone')
        
        form = super(DnaComponentAdmin,self).get_form(request, obj,**kwargs)

        field = form.base_fields['componentType']
        field.queryset = field.queryset.exclude(subTypeOf=None)
        field.initial = DnaComponentType.objects.get(name='generic plasmid').id
##        field.empty_label = '---specifiy type---'

        form.base_fields['insert'].queryset = \
            form.base_fields['insert'].queryset.filter(componentType__subTypeOf=typeInsert)
        form.base_fields['insert'].empty_label = '---no insert---'
        
        form.base_fields['marker'].queryset = \
            form.base_fields['marker'].queryset.filter(componentType__subTypeOf=typeMarker)
##        form.base_fields['marker'].empty_label = '---no marker---'
        ## form.base_fields['marker'].widget.widget.allow_multiple_selected = True
        form.base_fields['marker'].help_text = 'select multiple with Control/Command key'
        
        form.base_fields['vectorBackbone'].queryset = \
            form.base_fields['vectorBackbone'].queryset.filter(componentType__subTypeOf=typeVectorBB)
        form.base_fields['vectorBackbone'].empty_label = '---specifiy vector---'
        
        return form



admin.site.register(DnaComponent, DnaComponentAdmin)
admin.site.register(DnaComponentType)
