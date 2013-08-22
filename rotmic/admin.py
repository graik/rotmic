from django.contrib import admin

import datetime

from rotmic.models import DnaComponent, DnaComponentType
from rotmic.utils.customadmin import ViewFirstModelAdmin
from rotmic.forms import DnaComponentForm


class BaseAdminMixin():
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
                       ('registeredBy','registeredAt')
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

    list_display = ('displayId', 'name', 'registrationDate', 'registeredBy','insert','vectorBackbone', 'comment','status')

    def get_form(self, request, obj=None, **kwargs):
        """
        Override queryset of ForeignKey fields without overriding the field itself.
        This preserves the "+" Button which is otherwise lost.
        See http://djangosnippets.org/snippets/1558/#c4674
        """
        typeMarker = DnaComponentType.objects.get(name='Marker')
        typeInsert = DnaComponentType.objects.get(name='Insert')
        
        form = super(DnaComponentAdmin,self).get_form(request, obj,**kwargs)
        # form class is created per request by modelform_factory function
        # so it's safe to modify
        #we modify the the queryset
        form.base_fields['insert'].queryset = form.base_fields['insert'].queryset.filter(componentType__subTypeOf=typeInsert)
        form.base_fields['marker'].queryset = form.base_fields['marker'].queryset.filter(componentType__subTypeOf=typeMarker)
        return form



admin.site.register(DnaComponent, DnaComponentAdmin)
admin.site.register(DnaComponentType)
