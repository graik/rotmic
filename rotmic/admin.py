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


class DnaComponentAdmin( BaseAdminMixin, ViewFirstModelAdmin ):
    form = DnaComponentForm

    fieldsets = (
        (None, {
            'fields': (('displayId', 'name','status'),
                       ('componentType', 'circular',),
                       ('vectorBackbone','marker','insert' ),
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

    list_display = ('displayId', 'name', 'registeredBy','insert','vectorBackbone', 'comment','status')

admin.site.register(DnaComponent, DnaComponentAdmin)
admin.site.register(DnaComponentType)
