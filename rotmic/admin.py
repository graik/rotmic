from django.contrib import admin

import datetime

from rotmic.models import DnaComponent
from rotmic.utils.customadmin import ViewFirstModelAdmin


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
    pass

admin.site.register(DnaComponent, DnaComponentAdmin)
