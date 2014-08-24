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

import reversion

import rotmic.models as M
import rotmic.templatetags.rotmicfilters as F
from . import forms

from .utils import adminFilters as filters

from .adminBase import UserRecordMixin, RequestFormMixin, export_csv, UpdateManyMixin

class SequencingRunInline(admin.TabularInline):
    model = M.SequencingRun
    form = forms.SequencingRunForm
    extra = 2
    max_num = 15

    fieldsets = (
        (None,
         { 'fields': ('f', 'primer', 'description')
           }),
    )
    
class SequencingAdmin(UserRecordMixin, RequestFormMixin, reversion.VersionAdmin):
    form = forms.SequencingForm
    
    change_list_template = "admin/rotmic/sequencing/change_list.html"

    inlines = [ SequencingRunInline ]

    fieldsets = (
        (None,
         { 'fields': (('dummyfield',), ('sample','evaluation'),('orderedAt', 'orderedBy'), 
                      'comments')
           }),
    )

    ordering = ('sample', 'orderedAt')

    date_hierarchy = 'orderedAt'
    
    save_as = True
    save_on_top = True

    list_display   = ( '__unicode__', 'showSample', 'orderedAt', 'orderedBy', 'showEvaluation' )

    list_filter    = ('sample__dna__projects', filters.SortedOrderedByFilter, 'evaluation',)

    search_fields  = ('sample__displayId', 'sample__name', 'registeredBy__username',
                      'comments','evaluation',
                      'orderedBy__username',
                      'sample__container__displayId')
    
    def showSample(self, obj):
        """Table display of linked sample ''"""
        assert isinstance(obj, M.Sequencing), 'object missmatch'
        x = obj.sample
        if not x:
            return u''
        url = x.get_absolute_url()
        s = '%s (%s)' % ( x, x.content.displayId)
        return html.mark_safe('<a href="%s" title="">%s</a>' \
                              % (url, s ))
    showSample.allow_tags = True
    showSample.short_description = 'Sample'

admin.site.register(M.Sequencing, SequencingAdmin)